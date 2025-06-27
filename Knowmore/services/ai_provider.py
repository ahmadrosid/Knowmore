from .claude_service import ClaudeService
from .openai_service import OpenAIService


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
                'claude-3-5-sonnet-20240620',
                'claude-3-haiku-20240307',
                'claude-3-opus-20240229'
            ],
            'openai': [
                'gpt-3.5-turbo',
                'gpt-4',
                'gpt-4-turbo-preview'
            ]
        }