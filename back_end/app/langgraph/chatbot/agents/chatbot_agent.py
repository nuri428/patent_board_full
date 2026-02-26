"""
LangGraph chatbot agent implementation.
"""

from typing import Dict, List, Any, Optional, TypedDict, Annotated
from datetime import datetime, timezone
import uuid
import json
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings
from app.core.prompt_templates import PromptTemplates
from ..memory import (
    MemoryManager,
    UserProperty,
    ConversationSession,
    ConversationMessage,
)
from ..models.database import PropertyType
from .context_engineering import ContextEngineering


class ChatbotState(TypedDict):
    """State for the chatbot conversation"""

    user_id: str
    session_id: str
    messages: List[Dict[str, Any]]
    context: Dict[str, Any]
    user_properties: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    patent_context: Optional[Dict[str, Any]]
    response_mode: str
    max_tokens: int
    temperature: float


class ChatbotAgent:
    """LangGraph-based chatbot agent with context engineering"""

    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        memory_manager: Optional[MemoryManager] = None,
        context_engineering: Optional[ContextEngineering] = None,
    ):
        llm_config = {
            "model": settings.OPENAI_MODEL,
            "temperature": settings.OPENAI_TEMPERATURE,
            "top_p": settings.OPENAI_TOP_P,
            "frequency_penalty": settings.OPENAI_FREQUENCY_PENALTY,
            "presence_penalty": settings.OPENAI_PRESENCE_PENALTY,
            "api_key": settings.OPENAI_API_KEY,
        }

        # Add max_tokens if available (depends on langchain version)
        if hasattr(settings, "OPENAI_MAX_TOKENS") and settings.OPENAI_MAX_TOKENS:
            llm_config["max_tokens"] = settings.OPENAI_MAX_TOKENS

        self.llm = llm or ChatOpenAI(**llm_config)

        self.memory_manager = memory_manager
        self.context_engineering = context_engineering

        # Initialize memory saver for LangGraph
        self.checkpoint_memory = MemorySaver()

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        graph = StateGraph(ChatbotState)

        # Add nodes
        graph.add_node("load_context", self._load_context)
        graph.add_node("process_message", self._process_message)
        graph.add_node("enhance_context", self._enhance_context)
        graph.add_node("generate_response", self._generate_response)
        graph.add_node("save_memory", self._save_memory)
        graph.add_node("handle_patent_query", self._handle_patent_query)

        # Add edges
        graph.add_edge(START, "load_context")
        graph.add_edge("load_context", "process_message")
        graph.add_edge("process_message", "enhance_context")
        graph.add_edge("enhance_context", "handle_patent_query")
        graph.add_edge("handle_patent_query", "generate_response")
        graph.add_edge("generate_response", "save_memory")
        graph.add_edge("save_memory", END)

        # Compile the graph
        return graph.compile(
            checkpointer=self.checkpoint_memory,
            interrupt_before=None,
            interrupt_after=None,
        )

    async def _load_context(self, state: ChatbotState) -> ChatbotState:
        """Load user context and conversation history"""
        if not self.memory_manager:
            return state

        user_id = state["user_id"]

        # Load user properties
        user_properties = await self.memory_manager.get_user_properties(user_id)
        property_dict = {}
        for prop in user_properties:
            property_dict[prop.key] = {
                "value": prop.value,
                "type": prop.type,
                "updated_at": prop.updated_at.isoformat(),
            }

        # Load conversation history
        session = await self.memory_manager.get_conversation_session(
            state["session_id"]
        )
        conversation_history = []

        if session and session.messages:
            for message in session.messages:
                conversation_history.append(
                    {
                        "role": message.role,
                        "content": message.message,
                        "extra_metadata": message.extra_metadata or {},
                        "timestamp": message.timestamp.isoformat(),
                    }
                )

        # Update state
        state["user_properties"] = property_dict
        state["conversation_history"] = conversation_history

        return state

    async def _process_message(self, state: ChatbotState) -> ChatbotState:
        """Process the incoming message"""
        message = state["messages"][-1] if state["messages"] else {}
        content = message.get("content", "")

        # Update context with current message
        state["context"]["current_message"] = {
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "extra_metadata": message.get("extra_metadata", {}),
        }

        # Detect if this is a patent-related query
        if self.context_engineering:
            patent_intent = await self.context_engineering.detect_patent_intent(content)
            if patent_intent:
                state["context"]["patent_intent"] = patent_intent
                state["context"]["needs_patent_search"] = True

        return state

    async def _enhance_context(self, state: ChatbotState) -> ChatbotState:
        """Enhance context using context engineering"""
        if not self.context_engineering:
            return state

        user_id = state["user_id"]

        # Enhance with user preferences and history
        enhanced_context = await self.context_engineering.enhance_with_user_context(
            user_id, state["context"]
        )

        # Merge with existing context
        state["context"].update(enhanced_context)

        return state

    async def _handle_patent_query(self, state: ChatbotState) -> ChatbotState:
        """Handle patent-related queries using MCP integration"""
        if not state["context"].get("needs_patent_search"):
            return state

        if not self.context_engineering:
            return state

        try:
            # Extract patent query details
            query_content = state["context"]["current_message"]["content"]
            patent_context = await self.context_engineering.search_patents(
                query_content
            )

            # Add to state
            state["patent_context"] = patent_context
            state["context"]["patent_context"] = patent_context

            # Update conversation history
            if patent_context.get("results"):
                patent_summary = (
                    f"Found {len(patent_context['results'])} relevant patents"
                )
                state["conversation_history"].append(
                    {
                        "role": "system",
                        "content": patent_summary,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "extra_metadata": {
                            "type": "patent_search",
                            "result_count": len(patent_context["results"]),
                        },
                    }
                )

        except Exception as e:
            # Log error but continue
            state["context"]["error"] = f"Patent search failed: {str(e)}"

        return state

    async def _generate_response(self, state: ChatbotState) -> ChatbotState:
        """Generate AI response using the LLM"""
        # Prepare conversation history for the LLM
        conversation_for_llm = []

        # Add system message with context
        system_prompt = self._build_system_prompt(state)
        conversation_for_llm.append(SystemMessage(content=system_prompt))

        # Add conversation history
        for hist_msg in state["conversation_history"]:
            if hist_msg["role"] == "user":
                conversation_for_llm.append(HumanMessage(content=hist_msg["content"]))
            elif hist_msg["role"] == "assistant":
                conversation_for_llm.append(AIMessage(content=hist_msg["content"]))

        # Add current message
        current_message = state["messages"][-1]
        conversation_for_llm.append(HumanMessage(content=current_message["content"]))

        # Generate response
        try:
            response = await self.llm.ainvoke(conversation_for_llm)

            # Add response to state
            response_message = {
                "role": "assistant",
                "content": response.content,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "extra_metadata": {
                    "model": "gpt-4-turbo-preview",
                    "tokens_used": getattr(response, "usage", {}).get(
                        "total_tokens", 0
                    ),
                },
            }

            state["messages"].append(response_message)
            state["context"]["last_response"] = response_message

        except Exception as e:
            # Generate fallback response
            error_response = {
                "role": "assistant",
                "content": f"I apologize, but I encountered an error while processing your request: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "extra_metadata": {"error": str(e)},
            }
            state["messages"].append(error_response)

        return state

    async def _save_memory(self, state: ChatbotState) -> ChatbotState:
        """Save conversation to memory"""
        if not self.memory_manager:
            return state

        user_id = state["user_id"]
        session_id = state["session_id"]

        try:
            # Get current session
            session = await self.memory_manager.get_conversation_session(session_id)

            if not session:
                # Create new session
                session = ConversationSession(
                    id=session_id,
                    user_id=user_id,
                    title=state["context"].get("session_title", "New Conversation"),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    messages=[],
                    context=state["context"],
                )
                await self.memory_manager.create_conversation_session(session)
            else:
                # Update existing session
                session.context = state["context"]
                await self.memory_manager.update_conversation_session(session)

            # Save new messages
            for msg in state["messages"][-2:]:  # Save the user message and AI response
                if msg["role"] == "user":
                    message = ConversationMessage(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        session_id=session_id,
                        message=msg["content"],
                        role="user",
                        timestamp=datetime.fromisoformat(msg["timestamp"]),
                        extra_metadata=msg.get("extra_metadata", {}),
                    )
                elif msg["role"] == "assistant":
                    message = ConversationMessage(
                        id=str(uuid.uuid4()),
                        user_id="chatbot",
                        session_id=session_id,
                        message=msg["content"],
                        role="assistant",
                        timestamp=datetime.fromisoformat(msg["timestamp"]),
                        extra_metadata=msg.get("extra_metadata", {}),
                    )

                await self.memory_manager.add_message_to_session(session_id, message)

        except Exception as e:
            # Log error but don't fail the response
            state["context"]["memory_error"] = str(e)

        return state

    def _build_system_prompt(self, state: ChatbotState) -> str:
        """Build the system prompt for the LLM"""

        # Generate template sections
        user_preferences_section = PromptTemplates.get_user_preferences_section(
            state["user_properties"]
        )
        conversation_history_section = PromptTemplates.get_conversation_history_section(
            state["conversation_history"], limit=settings.CHATBOT_CONTEXT_HISTORY_LIMIT
        )
        patent_context_section = PromptTemplates.get_patent_context_section(
            state["patent_context"] or {}, limit=settings.CHATBOT_PATENT_CONTEXT_LIMIT
        )

        # Build the prompt using the template
        prompt = settings.CHATBOT_SYSTEM_PROMPT_TEMPLATE.format(
            user_preferences_section=user_preferences_section,
            conversation_history_section=conversation_history_section,
            patent_context_section=patent_context_section,
        )

        return prompt.strip()

    async def process_message(
        self,
        user_id: str,
        session_id: str,
        message_content: str,
        message_metadata: Optional[Dict[str, Any]] = None,
        initial_state: Optional[ChatbotState] = None,
    ) -> Dict[str, Any]:
        """Process a user message and return the response"""

        # Initialize state
        if not initial_state:
            initial_state = ChatbotState(
                user_id=user_id,
                session_id=session_id,
                messages=[],
                context={},
                user_properties={},
                conversation_history=[],
                patent_context=None,
                response_mode="standard",
                max_tokens=settings.CHATBOT_MAX_TOKENS,
                temperature=settings.CHATBOT_DEFAULT_TEMPERATURE,
            )

        # Add the user message
        initial_state["messages"].append(
            {
                "role": "user",
                "content": message_content,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "extra_metadata": message_metadata or {},
            }
        )

        # Run the graph
        try:
            result = await self.graph.ainvoke(initial_state)

            return {
                "success": True,
                "session_id": session_id,
                "response": result["messages"][-1] if result["messages"] else None,
                "context": result["context"],
                "user_properties": result["user_properties"],
                "total_messages": len(result["messages"]),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "response": None,
            }

    async def create_new_session(self, user_id: str, title: str = None) -> str:
        """Create a new conversation session"""

        session_id = str(uuid.uuid4())

        session = ConversationSession(
            id=session_id,
            user_id=user_id,
            title=title or "New Conversation",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            messages=[],
            context={},
        )

        if self.memory_manager:
            await self.memory_manager.create_conversation_session(session)

        return session_id

    async def get_conversation_summary(
        self, session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get conversation summary"""
        if not self.memory_manager:
            return None

        session = await self.memory_manager.get_conversation_session(session_id)
        if not session:
            return None

        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "message_count": len(session.messages),
            "context": session.context,
        }
