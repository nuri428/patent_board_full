from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import json
import uuid

from app.core.config import settings
from .mcp_client import mcp_client


class PatentAnalysisState(TypedDict):
    topic: str
    patent_ids: List[str]
    query_results: List[Dict[str, Any]]
    analysis_summary: str
    sections: Dict[str, str]
    final_report: str
    error: str


class PatentReportGenerator:
    def __init__(self):
        api_key = settings.OPENAI_API_KEY or "dummy-key"
        self.llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=api_key)
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(PatentAnalysisState)

        graph.add_node("collect_patents", self._collect_patents)
        graph.add_node("analyze_data", self._analyze_data)
        graph.add_node("generate_summary", self._generate_summary)
        graph.add_node("create_sections", self._create_sections)
        graph.add_node("compile_report", self._compile_report)

        graph.add_edge(START, "collect_patents")
        graph.add_edge("collect_patents", "analyze_data")
        graph.add_edge("analyze_data", "generate_summary")
        graph.add_edge("generate_summary", "create_sections")
        graph.add_edge("create_sections", "compile_report")
        graph.add_edge("compile_report", END)

        return graph.compile()

    async def _collect_patents(self, state: PatentAnalysisState) -> PatentAnalysisState:
        try:
            patent_data = []

            if state["patent_ids"]:
                for patent_id in state["patent_ids"]:
                    patent_info = await mcp_client.get_patent_details(patent_id)
                    if "error" not in patent_info:
                        patent_data.append(patent_info)
            else:
                search_results = await mcp_client.search_patents(
                    state["topic"], limit=20
                )
                patent_data = search_results

            state["query_results"] = patent_data
            return state

        except Exception as e:
            state["error"] = f"Patent collection failed: {str(e)}"
            return state

    async def _analyze_data(self, state: PatentAnalysisState) -> PatentAnalysisState:
        try:
            if not state["query_results"]:
                state["error"] = "No patent data to analyze"
                return state

            patents_text = "\n\n".join(
                [
                    f"Patent {p.get('patent_id', 'Unknown')}: {p.get('title', 'No title')}\n"
                    f"Abstract: {p.get('abstract', 'No abstract')[:500]}..."
                    for p in state["query_results"][:5]
                ]
            )

            analysis_prompt = f"""
            Analyze the following patents related to '{state["topic"]}':
            
            {patents_text}
            
            Provide a comprehensive analysis covering:
            1. Key technologies and innovations
            2. Market trends and applications
            3. Competitive landscape
            4. Legal and strategic considerations
            
            Analysis:
            """

            messages = [HumanMessage(content=analysis_prompt)]
            analysis = await self.llm.ainvoke(messages)

            state["analysis_summary"] = str(analysis.content)
            return state

        except Exception as e:
            state["error"] = f"Data analysis failed: {str(e)}"
            return state

    async def _generate_summary(
        self, state: PatentAnalysisState
    ) -> PatentAnalysisState:
        try:
            summary_prompt = f"""
            Create an executive summary for a patent analysis report on '{state["topic"]}'.
            
            Based on this analysis:
            {state["analysis_summary"]}
            
            The summary should be concise (200-300 words) and highlight key findings.
            
            Executive Summary:
            """

            messages = [HumanMessage(content=summary_prompt)]
            summary = await self.llm.ainvoke(messages)

            state["analysis_summary"] = str(summary.content)
            return state

        except Exception as e:
            state["error"] = f"Summary generation failed: {str(e)}"
            return state

    async def _create_sections(self, state: PatentAnalysisState) -> PatentAnalysisState:
        try:
            sections = {}

            section_prompts = {
                "technical_analysis": f"""
                Provide detailed technical analysis based on:
                {state["analysis_summary"]}
                
                Focus on: technologies, innovations, technical challenges.
                """,
                "market_landscape": f"""
                Analyze market landscape based on:
                {state["analysis_summary"]}
                
                Focus on: market size, trends, opportunities, threats.
                """,
                "strategic_recommendations": f"""
                Provide strategic recommendations based on:
                {state["analysis_summary"]}
                
                Focus on: R&D direction, IP strategy, business opportunities.
                """,
            }

            for section_name, prompt in section_prompts.items():
                messages = [HumanMessage(content=prompt)]
                section_content = await self.llm.ainvoke(messages)
                sections[section_name] = str(section_content.content)

            state["sections"] = sections
            return state

        except Exception as e:
            state["error"] = f"Section creation failed: {str(e)}"
            return state

    async def _compile_report(self, state: PatentAnalysisState) -> PatentAnalysisState:
        try:
            report_template = f"""
# Patent Analysis Report: {state["topic"]}

## Executive Summary
{state["analysis_summary"]}

## Technical Analysis
{state["sections"].get("technical_analysis", "No technical analysis available")}

## Market Landscape
{state["sections"].get("market_landscape", "No market analysis available")}

## Strategic Recommendations
{state["sections"].get("strategic_recommendations", "No recommendations available")}

## Patents Analyzed
{len(state["query_results"])} patents were analyzed in this report.
"""

            state["final_report"] = report_template
            return state

        except Exception as e:
            state["error"] = f"Report compilation failed: {str(e)}"
            return state

    async def generate_report(
        self, topic: str, patent_ids: List[str] = None
    ) -> Dict[str, Any]:
        patent_ids = patent_ids or []

        initial_state = PatentAnalysisState(
            topic=topic,
            patent_ids=patent_ids,
            query_results=[],
            analysis_summary="",
            sections={},
            final_report="",
            error="",
        )

        try:
            result = await self.graph.ainvoke(initial_state)

            if result.get("error"):
                return {"success": False, "error": result["error"]}

            return {
                "success": True,
                "report": result["final_report"],
                "patents_analyzed": len(result["query_results"]),
                "report_id": str(uuid.uuid4()),
            }

        except Exception as e:
            return {"success": False, "error": f"Report generation failed: {str(e)}"}


report_generator = PatentReportGenerator()
