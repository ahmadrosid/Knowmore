from typing import Dict, List, Type, Optional
from .base.tool import BaseTool
from .search.web_anthropic import AnthropicWebSearch
from .search.web_firecrawl import FirecrawlWebSearch

class ToolRegistry:
    """Registry for managing and discovering tools"""
    
    def __init__(self):
        self._tools: Dict[str, Type[BaseTool]] = {}
        self._instances: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register built-in tools"""
        self.register_tool("anthropic_web_search", AnthropicWebSearch)
        self.register_tool("firecrawl_web_search", FirecrawlWebSearch)
    
    def register_tool(self, name: str, tool_class: Type[BaseTool]):
        """Register a tool class"""
        self._tools[name] = tool_class
    
    def get_tool(self, name: str, **init_kwargs) -> Optional[BaseTool]:
        """Get tool instance by name"""
        if name not in self._tools:
            return None
        
        # Create instance key for caching
        instance_key = f"{name}_{hash(str(sorted(init_kwargs.items())))}"
        
        if instance_key not in self._instances:
            tool_class = self._tools[name]
            self._instances[instance_key] = tool_class(**init_kwargs)
        
        return self._instances[instance_key]
    
    def get_tools_for_provider(self, provider: str, **config) -> List[BaseTool]:
        """Get appropriate tools for a specific AI provider"""
        tools = []
        
        if provider.lower() in ["claude", "anthropic"]:
            # Anthropic models use native web search
            anthropic_search = self.get_tool("anthropic_web_search")
            if anthropic_search:
                tools.append(anthropic_search)
        
        elif provider.lower() in ["openai", "gpt"]:
            # OpenAI models use Firecrawl
            firecrawl_api_key = config.get("firecrawl_api_key")
            if firecrawl_api_key:
                firecrawl_search = self.get_tool("firecrawl_web_search", api_key=firecrawl_api_key)
                if firecrawl_search:
                    tools.append(firecrawl_search)
        
        return tools
    
    def get_tool_definitions_for_provider(self, provider: str, **config) -> List[Dict]:
        """Get tool definitions in the format required by the AI provider"""
        tools = self.get_tools_for_provider(provider, **config)
        
        if provider.lower() in ["claude", "anthropic"]:
            # Anthropic format
            return [tool.to_anthropic_tool() if hasattr(tool, 'to_anthropic_tool') else tool.to_dict() for tool in tools]
        else:
            # OpenAI format
            return [tool.to_dict() for tool in tools]
    
    def list_available_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self._tools.keys())
    
    def search_tools(self, category: str = None) -> List[str]:
        """Search tools by category"""
        if not category:
            return self.list_available_tools()
        
        # Simple category filtering based on tool names
        return [name for name in self._tools.keys() if category.lower() in name.lower()]

# Global registry instance
tool_registry = ToolRegistry()