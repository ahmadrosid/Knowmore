import json
import requests
import environ
from typing import Dict, Any, List

env = environ.Env(
    EXA_API_KEY=str,
)

class ExaWebSearch:
    def __init__(self):
        super().__init__()
        self.api_key = env("EXA_API_KEY", default="")
        self.base_url = "https://api.exa.ai"

    def get_name(self) -> str:
        return "web_search"

    def get_description(self) -> str:
        return "Search the web using Exa AI neural search and scrape content from results."

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
                "scrape_content": {
                    "type": "boolean",
                    "description": "Whether to scrape content from search results",
                    "default": False
                }
            },
            "required": ["query"]
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute Exa web search"""
        if not self.api_key:
            return {
                "error": "Exa API key not configured",
                "results": []
            }

        # Prepare request payload
        payload = {
            "query": kwargs["query"],
            "numResults": kwargs.get("limit", 5),
            "useAutoprompt": True,
        }

        # If scrape_content is requested, get page text contents too
        if kwargs.get("scrape_content", True):
            payload["contents"] = {
                "text": {
                    "maxCharacters": 5000
                }
            }

        try:
            response = requests.post(
                f"{self.base_url}/search",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key
                },
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                raw_results = data.get("results", [])
                
                # Transform to the structure expected by search orchestrator and UI
                formatted_results = []
                for result in raw_results:
                    title = result.get("title", "")
                    url = result.get("url", "")
                    
                    # Exa returns contents inside result when contents is set
                    text_content = ""
                    if "text" in result:
                        text_content = result["text"]
                    
                    formatted_results.append({
                        "title": title,
                        "url": url,
                        "markdown": text_content,
                        "description": text_content[:300] if text_content else ""
                    })

                return {
                    "success": True,
                    "results": formatted_results,
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
