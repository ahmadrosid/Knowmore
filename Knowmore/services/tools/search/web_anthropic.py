from typing import Dict, Any
from ..base.tool import BaseTool

class AnthropicWebSearch(BaseTool):
    """Anthropic native web search tool for Claude models"""
    
    def get_name(self) -> str:
        return "web_search"
    
    def get_description(self) -> str:
        return "Search the web for current information. Claude will automatically decide when to use this tool."
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "max_uses": {
                    "type": "integer",
                    "description": "Maximum number of searches to perform",
                    "default": 3
                },
                "allowed_domains": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of allowed domains for search results"
                },
                "blocked_domains": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of blocked domains for search results"
                },
                "user_location": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["approximate"]},
                        "city": {"type": "string"},
                        "region": {"type": "string"},
                        "country": {"type": "string"},
                        "timezone": {"type": "string"}
                    },
                    "description": "User location for localized search results"
                }
            },
            "required": ["query"]
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        For Anthropic's web search, this is handled automatically by the API.
        This method is mainly for consistency with the tool interface.
        """
        return {
            "type": "web_search",
            "parameters": kwargs
        }
    
    def to_anthropic_tool(self, max_uses=5, allowed_domains=None, blocked_domains=None, user_location=None) -> Dict[str, Any]:
        """Convert to Anthropic's tool format with configurable options"""
        tool_config = {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": max_uses
        }
        
        # Add optional domain filtering
        if allowed_domains:
            tool_config["allowed_domains"] = allowed_domains
        elif blocked_domains:
            tool_config["blocked_domains"] = blocked_domains
        
        # Add optional user location
        if user_location:
            tool_config["user_location"] = user_location
            
        return tool_config