"""
Prompt templates configuration for the patent analysis chatbot.
"""

from typing import Dict, Any


class PromptTemplates:
    """Collection of prompt templates for the chatbot system."""
    
    @staticmethod
    def get_system_prompt_template() -> str:
        """Get the main system prompt template."""
        return """
You are an AI assistant specialized in patent analysis and intellectual property. 
You help users understand patents, provide insights about patent landscapes, and assist with IP strategy.

Key guidelines:
1. Be accurate and specific in patent-related information
2. Provide context and explanations for technical concepts
3. If you mention patents, always cite the patent ID when available
4. Be helpful and informative about intellectual property concepts
5. Maintain professional tone suitable for IP professionals

User preferences and context:
{user_preferences_section}

Recent conversation context:
{conversation_history_section}

Relevant patents found:
{patent_context_section}
"""
    
    @staticmethod
    def get_user_preferences_section(user_properties: Dict[str, Any]) -> str:
        """Generate the user preferences section of the prompt."""
        if not user_properties:
            return ""
        
        section = "User preferences and context:\n"
        for key, prop in user_properties.items():
            if prop.get("type") in ["preference", "context"]:
                section += f"- {key}: {prop.get('value', 'N/A')}\n"
        return section + "\n"
    
    @staticmethod
    def get_conversation_history_section(conversation_history: list, limit: int = 5) -> str:
        """Generate the conversation history section of the prompt."""
        if not conversation_history:
            return ""
        
        section = "Recent conversation context:\n"
        for msg in conversation_history[-limit:]:  # Last N messages
            role = msg.get("role", "").lower()
            content = msg.get("content", "")
            if role == "user":
                section += f"User: {content}\n"
            elif role == "assistant":
                section += f"Assistant: {content}\n"
        return section + "\n"
    
    @staticmethod
    def get_patent_context_section(patent_context: Dict[str, Any], limit: int = 3) -> str:
        """Generate the patent context section of the prompt."""
        if not patent_context:
            return ""
        
        section = "Relevant patents found:\n"
        patents = patent_context.get("results", [])
        for patent in patents[:limit]:  # Top N patents
            patent_id = patent.get('patent_id', 'Unknown')
            title = patent.get('title', 'No title')
            section += f"- {patent_id}: {title}\n"
        return section + "\n"
    
    @staticmethod
    def get_patent_analysis_summary(analysis_result: Dict[str, Any]) -> str:
        """Generate a summary of patent analysis results."""
        if not analysis_result:
            return ""
        
        summary_parts = []
        
        # Add found patents summary
        found_patents = analysis_result.get("found", [])
        if found_patents:
            summary_parts.append(f"Found {len(found_patents)} patents in your message:")
            for patent in found_patents[:5]:  # Show top 5
                patent_id = patent.get("id", "Unknown")
                summary_parts.append(f"  - {patent_id}")
        
        # Add patent URLs if available
        urls = analysis_result.get("patent_urls", [])
        if urls:
            summary_parts.append(f"\nAvailable patent database links:")
            # Group URLs by patent
            patent_url_map = {}
            for url in urls:
                patent_id = url.get('patent_id', 'Unknown')
                if patent_id not in patent_url_map:
                    patent_url_map[patent_id] = []
                patent_url_map[patent_id].append(url)
            
            for patent_id, patent_urls in patent_url_map.items():
                source_urls = []
                for url_info in patent_urls[:2]:  # Show max 2 sources per patent
                    source = url_info.get('source', 'Unknown')
                    url = url_info.get('url', '')
                    source_urls.append(f"{source}: {url}")
                summary_parts.append(f"  • {patent_id}: {', '.join(source_urls)}")
        
        return "\n".join(summary_parts) if summary_parts else ""
    
    @staticmethod
    def get_user_interaction_patterns_summary(patterns: Dict[str, Any]) -> str:
        """Generate a summary of user interaction patterns."""
        if not patterns:
            return ""
        
        summary_parts = []
        
        if patterns.get("preferred_query_types"):
            summary_parts.append(f"Preferred query types: {', '.join(patterns['preferred_query_types'])}")
        
        if patterns.get("common_keywords"):
            summary_parts.append(f"Common keywords: {', '.join(patterns['common_keywords'][:5])}")  # Top 5
        
        if patterns.get("response_style_preference"):
            summary_parts.append(f"Response style preference: {patterns['response_style_preference']}")
        
        if patterns.get("patent_domain_focus"):
            summary_parts.append(f"Patent domain focus: {', '.join(patterns['patent_domain_focus'])}")
        
        return "\n".join(summary_parts) if summary_parts else ""
    
    @staticmethod
    def get_technical_preferences_summary(preferences: Dict[str, Any]) -> str:
        """Generate a summary of technical preferences."""
        if not preferences:
            return ""
        
        summary_parts = []
        
        if preferences.get("preferred_technologies"):
            summary_parts.append(f"Preferred technologies: {', '.join(preferences['preferred_technologies'][:5])}")  # Top 5
        
        if preferences.get("technical_depth"):
            summary_parts.append(f"Technical depth preference: {preferences['technical_depth']}")
        
        if preferences.get("focus_areas"):
            summary_parts.append(f"Focus areas: {', '.join(preferences['focus_areas'][:5])}")  # Top 5
        
        if preferences.get("language_preference"):
            summary_parts.append(f"Language preference: {preferences['language_preference']}")
        
        return "\n".join(summary_parts) if summary_parts else ""