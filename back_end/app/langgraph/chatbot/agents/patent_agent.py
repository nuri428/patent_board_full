"""
Patent Agent for specialized patent analysis and URL generation.
Handles patent identification, URL generation, and patent-specific context enhancement.
"""

from typing import Dict, List, Any, Optional, Tuple
import json
import re
from datetime import datetime


class PatentAgent:
    """Specialized agent for patent analysis and URL generation"""
    
    def __init__(self, mcp_client: Optional[Any] = None):
        self.mcp_client = mcp_client
        
    async def analyze_patent_text(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive patent text analysis with URL generation
        Returns extracted patents, URLs, and contextual information
        """
        result = {
            "patents_found": [],
            "urls_generated": [],
            "errors": [],
            "analysis_summary": {},
            "context_enhancement": {}
        }
        
        try:
            # Use MCP analyze_patent_text tool for comprehensive analysis
            if self.mcp_client:
                analysis_result = await self.mcp_client.analyze_patent_text(
                    text=text,
                    include_sources=["google", "uspto", "kipris", "wipo"]
                )
                
                if analysis_result and "summary" in analysis_result:
                    result["analysis_summary"] = analysis_result["summary"]
                    
                    if analysis_result["summary"].get("has_patents"):
                        # Extract patents found
                        if "extracted_patents" in analysis_result["summary"]:
                            result["patents_found"] = analysis_result["summary"]["extracted_patents"]
                        
                        # Extract generated URLs
                        if "generated_urls" in analysis_result["summary"]:
                            result["urls_generated"] = analysis_result["summary"]["generated_urls"]
                        
                        # Extract errors
                        if "errors" in analysis_result["summary"]:
                            result["errors"] = analysis_result["summary"]["errors"]
                
                # Add detailed context enhancement
                if "text_analysis" in analysis_result:
                    result["context_enhancement"]["text_analysis"] = analysis_result["text_analysis"]
                    
                if "url_generation" in analysis_result:
                    result["context_enhancement"]["url_generation"] = analysis_result["url_generation"]
                    
            else:
                # Fallback analysis without MCP
                result.update(await self._fallback_patent_analysis(text))
                
        except Exception as e:
            result["errors"].append(f"MCP analysis failed: {str(e)}")
            # Fallback analysis
            result.update(await self._fallback_patent_analysis(text))
        
        return result
    
    async def _fallback_patent_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback patent analysis when MCP is not available"""
        result = {
            "patents_found": [],
            "urls_generated": [],
            "errors": [],
            "analysis_summary": {},
            "context_enhancement": {}
        }
        
        try:
            # Basic regex extraction
            patent_patterns = [
                r'\bUS\d{6,}\b',  # US patents: US1234567
                r'\bKR\d{2}\d{4}\d{7}\b',  # KR patents: KR1020230001234
                r'\bWO\d{4}\d{6,}[A-Z]?\d*\b',  # WIPO patents: WO2023056789A1
                r'\b(?:EP|JP|CN|CA|AU|DE|FR|GB|IL|RU)\d{6,}\b'  # Other country patents
            ]
            
            found_patents = []
            for pattern in patent_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    found_patents.append({
                        "id": match.upper(),
                        "country": self._detect_country(match),
                        "type": "utility",
                        "raw_text": match
                    })
            
            # Remove duplicates
            unique_patents = []
            seen_ids = set()
            for patent in found_patents:
                if patent["id"] not in seen_ids:
                    unique_patents.append(patent)
                    seen_ids.add(patent["id"])
            
            result["patents_found"] = unique_patents
            result["analysis_summary"] = {
                "has_patents": len(unique_patents) > 0,
                "patent_count": len(unique_patents),
                "patents_found": len(unique_patents)
            }
            
            # Generate basic URLs for found patents
            for patent in unique_patents:
                try:
                    country = patent["country"]
                    patent_id = patent["id"]
                    
                    # Generate Google Patents URL
                    if country == "US":
                        url = f"https://patents.google.com/patent/{patent_id}"
                    elif country == "KR":
                        url = f"https://patents.google.com/patent/{patent_id}"
                    elif country == "WIPO":
                        url = f"https://patents.google.com/patent/{patent_id}"
                    else:
                        url = f"https://patents.google.com/patent/{country}{patent_id[2:] if patent_id.startswith(country) else patent_id}"
                    
                    result["urls_generated"].append({
                        "url": url,
                        "title": "Google Patents",
                        "source": "google",
                        "country": country,
                        "patent_id": patent_id
                    })
                    
                except Exception as e:
                    result["errors"].append(f"Failed to generate URL for {patent['id']}: {str(e)}")
        
        except Exception as e:
            result["errors"].append(f"Fallback analysis failed: {str(e)}")
        
        return result
    
    def _detect_country(self, patent_id: str) -> str:
        """Detect country from patent ID"""
        patent_id = patent_id.upper()
        
        if patent_id.startswith("US"):
            return "US"
        elif patent_id.startswith("KR"):
            return "KR"
        elif patent_id.startswith("WO"):
            return "WIPO"
        elif patent_id.startswith("EP"):
            return "EP"
        elif patent_id.startswith("JP"):
            return "JP"
        elif patent_id.startswith("CN"):
            return "CN"
        elif patent_id.startswith("CA"):
            return "CA"
        elif patent_id.startswith("AU"):
            return "AU"
        elif patent_id.startswith("DE"):
            return "DE"
        elif patent_id.startswith("FR"):
            return "FR"
        elif patent_id.startswith("GB"):
            return "GB"
        elif patent_id.startswith("IL"):
            return "IL"
        elif patent_id.startswith("RU"):
            return "RU"
        else:
            return "GENERIC"
    
    async def enhance_chat_response(self, user_message: str, base_response: str) -> str:
        """
        Enhance chat response with patent information and URLs
        Automatically detects patent IDs in user message and adds relevant links
        """
        enhanced_response = base_response
        
        try:
            # Analyze user message for patent IDs
            patent_analysis = await self.analyze_patent_text(user_message)
            
            if patent_analysis["patents_found"] and patent_analysis["urls_generated"]:
                # Add patent information to response
                enhanced_response += "\n\n📄 Related Patent Links:\n"
                
                # Group URLs by patent
                patent_url_map = {}
                for url in patent_analysis["urls_generated"]:
                    patent_id = url.get("patent_id", "Unknown")
                    if patent_id not in patent_url_map:
                        patent_url_map[patent_id] = []
                    patent_url_map[patent_id].append(url)
                
                # Format patent links
                for patent_id, urls in patent_url_map.items():
                    enhanced_response += f"\n🔍 **{patent_id}**\n"
                    for url_info in urls[:3]:  # Show max 3 sources
                        source = url_info.get("source", "Google")
                        url = url_info.get("url", "")
                        enhanced_response += f"  • [{source}]({url})\n"
                
                # Add helpful note
                enhanced_response += "\n💡 These links will take you to official patent databases for detailed information."
                
        except Exception as e:
            # If enhancement fails, return original response
            print(f"Error enhancing chat response: {e}")
        
        return enhanced_response
    
    async def get_patent_intelligence(self, patent_ids: List[str]) -> Dict[str, Any]:
        """
        Get comprehensive patent intelligence including details and URLs
        """
        result = {
            "patents": [],
            "urls": [],
            "intelligence_summary": {},
            "errors": []
        }
        
        try:
            for patent_id in patent_ids:
                patent_info = {"patent_id": patent_id}
                
                # Get patent details if MCP available
                if self.mcp_client:
                    try:
                        details = await self.mcp_client.get_patent_details(
                            patent_id=patent_id,
                            type="auto"  # Auto-detect type
                        )
                        if details and "data" in details:
                            patent_info.update(details["data"])
                    except Exception as e:
                        result["errors"].append(f"Failed to get details for {patent_id}: {e}")
                
                # Generate URLs
                try:
                    country = self._detect_country(patent_id)
                    url_result = await self.mcp_client.generate_patent_urls(
                        patent_ids=[patent_id],
                        country=country,
                        sources=["google", "uspto", "kipris", "wipo"]
                    )
                    
                    if url_result and "urls" in url_result:
                        patent_info["urls"] = url_result["urls"]
                        result["urls"].extend(url_result["urls"])
                        
                except Exception as e:
                    result["errors"].append(f"Failed to generate URLs for {patent_id}: {e}")
                
                result["patents"].append(patent_info)
            
            # Generate intelligence summary
            if result["patents"]:
                result["intelligence_summary"] = {
                    "total_patents": len(result["patents"]),
                    "countries_found": list(set(p.get("country", "Unknown") for p in result["patents"])),
                    "total_urls": len(result["urls"]),
                    "unique_sources": list(set(u.get("source", "Unknown") for u in result["urls"]))
                }
        
        except Exception as e:
            result["errors"].append(f"Intelligence analysis failed: {str(e)}")
        
        return result