import os
from .registry import tool_registry


class ProviderTools:
    """Helper class for getting tools for different AI providers"""
    
    @staticmethod
    def get_available_tools(model_name, **config):
        """Get available tools for a specific model"""
        if model_name.startswith('claude'):
            return tool_registry.get_tools_for_provider('claude', **config)
        elif model_name.startswith('gpt'):
            return tool_registry.get_tools_for_provider('openai', **config)
        else:
            return tool_registry.get_tools_for_provider('claude', **config)
    
    @staticmethod
    def get_tool_definitions(model_name, **config):
        """Get tool definitions in the format required by the model's API"""
        if model_name.startswith('claude'):
            return tool_registry.get_tool_definitions_for_provider('claude', **config)
        elif model_name.startswith('gpt'):
            return tool_registry.get_tool_definitions_for_provider('openai', **config)
        else:
            return tool_registry.get_tool_definitions_for_provider('claude', **config)