import httpx
from typing import Any, Dict
from app.core.config import settings
from app.schemas.mcp import ProxyResult


class MCPService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = settings.MCP_SERVER_URL

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ProxyResult:
        """
        Call a tool on the MCP server.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/tools/{tool_name}",
                    json=arguments,
                    headers={
                        "X-API-Key": self.api_key,
                        "X-Request-Source": "human-proxy",
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                raw_data = response.json()
                return self._process_response(tool_name, raw_data)
        except Exception as e:
            # Re-raise or handle appropriately. For simplicity, we'll let the endpoint handle fallback
            # or we can move the fallback logic here if desired.
            # Based on the current mcp.py, there is some fallback logic.
            raise e

    def _process_response(self, tool_name: str, raw_data: Any) -> ProxyResult:
        """
        Process raw MCP response: Bucketize scores and sample graph data.
        """
        confidence = "Medium"  # Default
        interpretation_note = None
        source = "KIPRIS (via MCP)"

        # Extract data from standardized wrapper if present
        content = raw_data
        if isinstance(raw_data, dict) and "status" in raw_data and "data" in raw_data:
            content = raw_data["data"]
            source = raw_data.get("metadata", {}).get("engine", source)
            if "confidence" in raw_data.get("metadata", {}):
                confidence = raw_data["metadata"]["confidence"]

        # 1. Score-based Confidence (if not provided by MCP)
        if confidence == "Medium" and isinstance(content, dict) and "score" in content:
            score = content.get("score", 0)
            if score > 0.8:
                confidence = "High"
            elif score < 0.4:
                confidence = "Low"

        # 2. Graph Sampling (Human UI optimization)
        if "graph" in tool_name or (isinstance(content, dict) and "nodes" in content):
            if isinstance(content, dict):
                nodes = content.get("nodes", [])
                edges = content.get("edges", [])

                # Sample for UI performance
                if len(nodes) > 30:
                    # Basic sampling: take the first 30 (assuming they might be ranked)
                    content["nodes"] = nodes[:30]
                    sampled_node_ids = {n.get("id") for n in content["nodes"]}
                    content["edges"] = [
                        e
                        for e in edges
                        if e.get("from") in sampled_node_ids
                        and e.get("to") in sampled_node_ids
                    ]
                    interpretation_note = (
                        f"Showing top 30 nodes out of {len(nodes)} for performance."
                    )
                elif len(nodes) > 0:
                    interpretation_note = f"Displaying {len(nodes)} nodes."

        return ProxyResult(
            status="success",
            data=content,
            confidence=confidence,
            interpretation_note=interpretation_note,
            source=source,
        )

    async def semantic_search(self, query: str, limit: int) -> ProxyResult:
        return await self.call_tool(
            "search_kr_patents",
            {"query": query, "limit": limit, "year_start": None, "year_end": None},
        )

    async def network_analysis(self, params: Dict[str, Any]) -> ProxyResult:
        return await self.call_tool("run_network_analysis", params)

    async def technology_mapping(self, params: Dict[str, Any]) -> ProxyResult:
        return await self.call_tool("create_technology_mapping", params)
