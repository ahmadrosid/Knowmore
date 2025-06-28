from .claude_service import ClaudeService
from .openai_service import OpenAIService
from .tools.registry import tool_registry


class AIProviderFactory:
    @staticmethod
    def get_provider(model_name):
        if model_name.startswith('claude'):
            return ClaudeService()
        elif model_name.startswith('gpt'):
            return OpenAIService()
        else:
            # Default to Claude
            return ClaudeService()

    @staticmethod
    def get_supported_models():
        return {
            'claude': [
                'claude-opus-4-20250514',
                'claude-sonnet-4-20250514',
                'claude-3-7-sonnet-20250219'
            ],
            'openai': [
                'gpt-4o-2024-08-06',
                'o4-mini-2025-04-16',
                'gpt-4.1-2025-04-14'
            ]
        }
    
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