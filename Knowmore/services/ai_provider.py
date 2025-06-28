from .claude_service import ClaudeService
from .openai_service import OpenAIService


class AIProviderFactory:
    @staticmethod
    def get_provider(model_name):
        if model_name.startswith('claude'):
            return ClaudeService()
        elif model_name.startswith('gpt') or model_name.startswith('o4'):
            return OpenAIService()
        else:
            # Default to Claude
            return ClaudeService()

    @staticmethod
    def get_supported_models():
        return {
            'claude': [
                {'id': 'claude-opus-4-20250514', 'name': 'Claude Opus 4'},
                {'id': 'claude-sonnet-4-20250514', 'name': 'Claude Sonnet 4'},
                {'id': 'claude-3-7-sonnet-20250219', 'name': 'Claude Sonnet 3.7'},
                {'id': 'claude-3-5-sonnet-latest', 'name': 'Claude Sonnet 3.5'},
                {'id': 'claude-3-5-haiku-latest', 'name': 'Claude Haiku 3.5'},
                {'id': 'claude-3-5-sonnet-20240620', 'name': 'Claude Sonnet 3.5'}
            ],
            'openai': [
                {'id': 'gpt-4o-2024-08-06', 'name': 'GPT-4o'},
                {'id': 'o4-mini-2025-04-16', 'name': 'O4 Mini'},
                {'id': 'gpt-4.1-2025-04-14', 'name': 'GPT-4.1'}
            ]
        }