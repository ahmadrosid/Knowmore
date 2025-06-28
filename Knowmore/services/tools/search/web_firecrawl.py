import json
import requests
from typing import Dict, Any, List
from ..base.tool import BaseTool

class FirecrawlWebSearch(BaseTool):
    """Firecrawl web search tool for OpenAI and other models"""
    
    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://api.firecrawl.dev/v1"
    
    def get_name(self) -> str:
        return "web_search"
    
    def get_description(self) -> str:
        return "Search the web and optionally scrape content from search results. Returns titles, descriptions, URLs and optional content."
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of search results to return",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 20
                },
                "location": {
                    "type": "string",
                    "description": "Location for localized search results (e.g., 'Germany', 'United States')"
                },
                "tbs": {
                    "type": "string",
                    "description": "Time-based search filter",
                    "enum": ["qdr:h", "qdr:d", "qdr:w", "qdr:m", "qdr:y"]
                },
                "scrape_content": {
                    "type": "boolean",
                    "description": "Whether to scrape content from search results",
                    "default": False
                },
                "formats": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["markdown", "html", "rawHtml", "links", "screenshot"]
                    },
                    "description": "Content formats to scrape (only used if scrape_content is true)",
                    "default": ["markdown"]
                }
            },
            "required": ["query"]
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute Firecrawl web search"""
        if not self.api_key:
            return {
                "error": "Firecrawl API key not configured",
                "results": []
            }
        
        # Prepare request payload
        payload = {
            "query": kwargs["query"],
            "limit": kwargs.get("limit", 5)
        }
        
        # Add optional parameters
        if "location" in kwargs:
            payload["location"] = kwargs["location"]
        if "tbs" in kwargs:
            payload["tbs"] = kwargs["tbs"]
        
        # Add scraping options if requested
        if kwargs.get("scrape_content", False):
            payload["scrapeOptions"] = {
                "formats": kwargs.get("formats", ["markdown"])
            }
        
        try:
            response = requests.post(
                f"{self.base_url}/search",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "results": data.get("data", []),
                    "query": kwargs["query"]
                }
            else:
                return {
                    "error": f"Search failed with status {response.status_code}",
                    "details": response.text,
                    "results": []
                }
                
        except requests.RequestException as e:
            return {
                "error": f"Network error: {str(e)}",
                "results": []
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "results": []
            }