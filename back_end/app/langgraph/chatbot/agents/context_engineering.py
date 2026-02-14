"""
Context Engineering module for patent analysis chatbot.
Enhances context understanding and integrates with MCP for patent data.
"""

from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import logging
from app.core.config import settings


logger = logging.getLogger(__name__)


class ContextEngineering:
    """Handles context engineering for patent-related queries"""
    
    def __init__(self, mcp_client: Optional[Any] = None):
        self.mcp_client = mcp_client
        self.patent_keywords = settings.CONTEXT_ENGINEERING_PATENT_KEYWORDS
        
        self.technology_domains = settings.CONTEXT_ENGINEERING_TECHNOLOGY_DOMAINS
        
        self.patent_verbs = settings.CONTEXT_ENGINEERING_PATENT_VERBS
        
        self.patent_id_pattern = settings.CONTEXT_ENGINEERING_PATENT_ID_PATTERN
        
        self.user_pattern_analysis_enabled = settings.USER_PATTERN_ANALYSIS_ENABLED
        self.user_pattern_keyword_threshold = settings.USER_PATTERN_KEYWORD_THRESHOLD
        self.user_pattern_patent_id_threshold = settings.USER_PATTERN_PATENT_ID_THRESHOLD
        self.user_pattern_verb_threshold = settings.USER_PATTERN_VERB_THRESHOLD
        
        self.technical_complexity_terms = settings.TECHNICAL_COMPLEXITY_TERMS
        
        self.url_generation_sources = settings.URL_GENERATION_SOURCES
        self.url_generation_default_country = settings.URL_GENERATION_DEFAULT_COUNTRY
    
    async def detect_patent_intent(self, text: str) -> Dict[str, Any]:
        """Detect if the user's message has patent-related intent"""
        
        # Convert to lowercase for case-insensitive matching
        lower_text = text.lower()
        
        # Check for patent keywords
        found_keywords = []
        for keyword in self.patent_keywords:
            if keyword in lower_text:
                found_keywords.append(keyword)
        
        # Check for technology domains
        detected_domains = []
        for domain, keywords in self.technology_domains.items():
            domain_found = False
            for keyword in keywords:
                if keyword.lower() in lower_text:
                    domain_found = True
                    break
            if domain_found:
                detected_domains.append(domain)
        
        # Extract patent IDs using MCP tools with URL generation
        patent_ids = []
        patent_urls = []
        
        if self.mcp_client:
            try:
                extraction_result = await self.mcp_client.extract_patent_ids(text)
                if extraction_result and "found" in extraction_result:
                    for patent in extraction_result["found"]:
                        patent_ids.append(patent["id"])
                        # Generate URLs for extracted patents
                        try:
                            url_result = await self.mcp_client.generate_patent_urls(
                                patent_ids=[patent["id"]], 
                                country=patent["country"], 
                                sources=self.url_generation_sources
                            )
                            if url_result and "urls" in url_result:
                                patent_urls.extend(url_result["urls"])
                        except Exception:
                            logger.exception(
                                "Error generating URLs for extracted patent %s",
                                patent.get("id", "unknown"),
                            )
            except Exception:
                logger.exception("Error extracting patent IDs")
                # Fallback to regex pattern
                patent_ids = re.findall(self.patent_id_pattern, text)
        
        # Check for patent-related verbs
        found_verbs = []
        for verb in self.patent_verbs:
            if verb in lower_text:
                found_verbs.append(verb)
        
        return {
            "has_patent_intent": len(found_keywords) > 0 or len(patent_ids) > 0,
            "keywords": found_keywords,
            "domains": detected_domains,
            "patent_ids": patent_ids,
            "patent_urls": patent_urls,
            "verbs": found_verbs,
            "confidence": self._calculate_confidence(found_keywords, patent_ids, found_verbs),
            "query_type": self._classify_query_type(text)
        }
    
    def _calculate_confidence(self, keywords: List[str], patent_ids: List[str], verbs: List[str]) -> float:
        """Calculate confidence score for patent intent"""
        confidence = 0.0
        
        # Base confidence from keywords
        confidence += min(len(keywords) * 0.2, 0.4)
        
        # High confidence from patent IDs
        confidence += min(len(patent_ids) * 0.3, 0.6)
        
        # Boost from patent-related verbs
        confidence += min(len(verbs) * 0.1, 0.2)
        
        return min(confidence, 1.0)
    
    def _classify_query_type(self, text: str) -> str:
        """Classify the type of patent query"""
        lower_text = text.lower()
        
        if any(word in lower_text for word in ["search", "find", "lookup"]):
            if any(word in lower_text for word in ["similar", "related", "like"]):
                return "similarity_search"
            elif any(word in lower_text for word in ["by inventor", "by assignee", "by company"]):
                return "search_by_assignee"
            elif any(word in lower_text for word in ["by keyword", "by topic"]):
                return "keyword_search"
            else:
                return "general_search"
        
        elif any(word in lower_text for word in ["analyze", "explain", "understand"]):
            return "analysis"
        
        elif any(word in lower_text for word in ["compare", "difference"]):
            return "comparison"
        
        elif any(word in lower_text for word in ["market", "commercial", "business"]):
            return "commercial_analysis"
        
        else:
            return "general"
    
    async def enhance_with_user_context(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context with user-specific information"""
        
        enhanced_context = context.copy()
        
        # Add user interaction history
        enhanced_context["user_interaction_patterns"] = await self._analyze_user_patterns(user_id)
        
        # Add technical preferences
        enhanced_context["technical_preferences"] = await self._get_user_technical_preferences(user_id)
        
        # Add conversation context from history
        enhanced_context["historical_context"] = await self._get_historical_context(user_id)
        
        # Add user expertise level
        enhanced_context["expertise_level"] = await self._assess_user_expertise(user_id)
        
        return enhanced_context
    
    async def _analyze_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user interaction patterns"""
        # This would typically query the memory system for user behavior patterns
        # For now, return a basic structure
        return {
            "preferred_query_types": [],
            "common_keywords": [],
            "response_style_preference": "detailed",
            "patent_domain_focus": []
        }
    
    async def _get_user_technical_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user's technical preferences"""
        # This would typically query user properties
        return {
            "preferred_technologies": [],
            "technical_depth": "intermediate",
            "focus_areas": [],
            "language_preference": "english"
        }
    
    async def _get_historical_context(self, user_id: str) -> Dict[str, Any]:
        """Get historical conversation context"""
        # This would typically query conversation history
        return {
            "recent_topics": [],
            "discussed_patents": [],
            "repeated_questions": [],
            "learning_progress": {}
        }
    
    async def _assess_user_expertise(self, user_id: str) -> str:
        """Assess user's expertise level based on their queries"""
        # This would analyze query complexity, terminology usage, etc.
        return "intermediate"
    
    async def search_patents(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for patents using MCP integration"""
        
        if not self.mcp_client:
            return {
                "success": False,
                "error": "MCP client not available",
                "results": []
            }
        
        try:
            # Detect query type and optimize search strategy
            intent = await self.detect_patent_intent(query)
            
            # If specific patent IDs mentioned, use get_patent_details instead
            if intent["patent_ids"]:
                return await self._get_patent_details_batch(intent["patent_ids"])
            
            # Perform patent search
            if intent["query_type"] == "similarity_search":
                # Use semantic search if available
                if hasattr(self.mcp_client, 'semantic_search'):
                    results = await self.mcp_client.semantic_search(
                        query=query,
                        limit=limit
                    )
                else:
                    results = await self.mcp_client.search_patents(
                        query=query,
                        limit=limit
                    )
            else:
                # Standard keyword search
                results = await self.mcp_client.search_patents(
                    query=query,
                    limit=limit
                )
            
            # Enhance results with context engineering
            enhanced_results = await self._enhance_patent_results(results, intent)
            
            return {
                "success": True,
                "query": query,
                "query_type": intent["query_type"],
                "results": enhanced_results,
                "total_results": len(results) if results else 0,
                "search_metadata": {
                    "keywords_found": intent["keywords"],
                    "domains_detected": intent["domains"],
                    "confidence": intent["confidence"]
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    async def _get_patent_details_batch(self, patent_ids: List[str]) -> Dict[str, Any]:
        """Get details for multiple patent IDs with URLs"""
        results = []
        all_urls = []
        
        for patent_id in patent_ids:
            try:
                details = await self.mcp_client.get_patent_details(patent_id)
                if details and "error" not in details:
                    results.append(details)
                    
                    # Generate URLs for this patent
                    try:
                        # Detect country from patent ID
                        country = "auto"
                        if patent_id.startswith("US"):
                            country = "US"
                        elif patent_id.startswith("KR"):
                            country = "KR"
                        elif patent_id.startswith("WO"):
                            country = "WIPO"
                        
                        url_result = await self.mcp_client.generate_patent_urls(
                            patent_ids=[patent_id],
                            country=country,
                            sources=self.url_generation_sources
                        )
                        if url_result and "urls" in url_result:
                            all_urls.extend(url_result["urls"])
                            
                            # Add URLs to patent details
                            if "data" in details and isinstance(details["data"], dict):
                                details["data"]["patent_urls"] = url_result["urls"]
                            
                    except Exception:
                        logger.exception(
                            "Error generating URLs for patent %s", patent_id
                        )

            except Exception:
                # Log error but continue with other patents
                logger.exception("Error fetching patent %s", patent_id)
        
        return {
            "success": True,
            "query_type": "specific_patents",
            "results": results,
            "total_results": len(results),
            "patent_urls": all_urls
        }
    
    def _map_query_type_to_search(self, query_type: str) -> str:
        """Map internal query type to MCP search type"""
        mapping = {
            "general_search": "keyword",
            "similarity_search": "semantic",
            "keyword_search": "keyword",
            "analysis": "keyword",
            "comparison": "keyword",
            "commercial_analysis": "keyword"
        }
        return mapping.get(query_type, "keyword")
    
    async def _enhance_patent_results(self, results: List[Dict[str, Any]], intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance patent search results with additional context"""
        
        enhanced_results = []
        
        for result in results:
            enhanced_result = result.copy()
            
            # Add relevance score based on query intent
            relevance_score = self._calculate_relevance_score(result, intent)
            enhanced_result["relevance_score"] = relevance_score
            
            # Add domain matching
            domain_matches = self._calculate_domain_matches(result, intent)
            enhanced_result["domain_matches"] = domain_matches
            
            # Add technical complexity assessment
            complexity = self._assess_technical_complexity(result)
            enhanced_result["technical_complexity"] = complexity
            
            # Add recentness score
            recentness = self._calculate_recentness_score(result)
            enhanced_result["recentness_score"] = recentness
            
            enhanced_results.append(enhanced_result)
        
        # Sort by relevance score
        enhanced_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return enhanced_results
    
    def _calculate_relevance_score(self, patent: Dict[str, Any], intent: Dict[str, Any]) -> float:
        """Calculate relevance score for a patent based on query intent"""
        score = 0.0
        
        # Check title and abstract relevance
        text_to_check = f"{patent.get('title', '')} {patent.get('abstract', '')}".lower()
        
        # Score for matching keywords
        for keyword in intent.get("keywords", []):
            if keyword in text_to_check:
                score += 0.3
        
        # Score for domain matches
        for domain in intent.get("domains", []):
            domain_keywords = self.technology_domains.get(domain, [])
            for keyword in domain_keywords:
                if keyword.lower() in text_to_check:
                    score += 0.5
        
        # Score for specific patent IDs (perfect match)
        if patent.get("patent_id") in intent.get("patent_ids", []):
            score += 1.0
        
        return min(score, 1.0)
    
    def _calculate_domain_matches(self, patent: Dict[str, Any], intent: Dict[str, Any]) -> List[str]:
        """Calculate which technology domains match the patent"""
        matches = []
        
        patent_text = f"{patent.get('title', '')} {patent.get('abstract', '')}".lower()
        
        for domain, keywords in self.technology_domains.items():
            for keyword in keywords:
                if keyword.lower() in patent_text:
                    matches.append(domain)
                    break
        
        return matches
    
    def _assess_technical_complexity(self, patent: Dict[str, Any]) -> str:
        """Assess technical complexity of a patent"""
        abstract = patent.get('abstract', '')
        
        # Simple heuristics for complexity assessment
        if len(abstract) < 200:
            return "simple"
        
        found_terms = sum(1 for term in self.technical_complexity_terms if term.lower() in abstract.lower())
        
        if found_terms >= 5:
            return "complex"
        elif found_terms >= 2:
            return "intermediate"
        else:
            return "simple"
    
    def _calculate_recentness_score(self, patent: Dict[str, Any]) -> float:
        """Calculate recentness score based on filing/grant date"""
        # This would need proper date parsing and calculation
        # For now, return a simple score based on year if available
        filing_date = patent.get('filing_date')
        if filing_date:
            try:
                # Extract year from date string (simplified)
                year = int(filing_date[:4]) if len(filing_date) >= 4 else 2020
                current_year = datetime.now().year
                age = current_year - year
                return max(0, 1 - age / 20)  # Decay over 20 years
            except (ValueError, TypeError):
                return 0.5
        
        return 0.5
    
    async def generate_contextual_summary(self, patents: List[Dict[str, Any]], context: Dict[str, Any], patent_urls: Optional[List[Dict[str, Any]]] = None) -> str:
        """Generate a contextual summary of patent results with URLs"""
        
        if not patents:
            return "No relevant patents found."
        
        # Group patents by technology domain
        domain_groups = {}
        for patent in patents:
            domains = patent.get("domain_matches", [])
            for domain in domains:
                if domain not in domain_groups:
                    domain_groups[domain] = []
                domain_groups[domain].append(patent)
        
        # Generate summary
        summary_parts = []
        
        summary_parts.append(f"Found {len(patents)} relevant patents:")
        
        # Summary by domain
        for domain, patents_in_domain in domain_groups.items():
            summary_parts.append(f"\n{domain.upper()} patents ({len(patents_in_domain)}):")
            
            # Show top patents in each domain
            for patent in patents_in_domain[:2]:
                title = patent.get('title', 'No title')
                patent_id = patent.get('patent_id', 'Unknown ID')
                complexity = patent.get('technical_complexity', 'unknown')
                
                summary_parts.append(f"- {patent_id}: {title[:80]}... ({complexity})")
        
        # Add patent URLs if available
        if patent_urls:
            summary_parts.append("\n📄 Patent Database Links:")
            # Group URLs by patent
            patent_url_map = {}
            for url in patent_urls:
                patent_id = url.get('patent_id', 'Unknown')
                if patent_id not in patent_url_map:
                    patent_url_map[patent_id] = []
                patent_url_map[patent_id].append(url)
            
            for patent_id, urls in patent_url_map.items():
                source_urls = []
                for url_info in urls[:2]:  # Show max 2 sources per patent
                    source = url_info.get('source', 'Unknown')
                    url = url_info.get('url', '')
                    source_urls.append(f"{source}: {url}")
                summary_parts.append(f"  • {patent_id}: {', '.join(source_urls)}")
        
        # Add insights based on query context
        if context.get("patent_intent", {}).get("query_type") == "similarity_search":
            summary_parts.append("\nThis search focused on finding similar technologies and innovations.")
        
        return "\n".join(summary_parts)
