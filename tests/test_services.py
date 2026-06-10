import unittest
import os
import sys
import json
import environ
from unittest.mock import AsyncMock, MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load .env file into environment
environ.Env.read_env(os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env')))

# Set Django settings module so imports don't crash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Knowmore.settings')
import django
django.setup()

from Knowmore.services.ai_provider import AIProviderFactory
from Knowmore.services.openrouter_service import OpenRouterService
from Knowmore.services.web_search_exa import ExaWebSearch
from Knowmore.services.search_orchestrator import SearchOrchestrator

class TestAIProviderFactory(unittest.TestCase):
    def test_get_supported_models(self):
        models = AIProviderFactory.get_supported_models()
        self.assertIn('openrouter', models)
        openrouter_models = models['openrouter']
        self.assertEqual(len(openrouter_models), 4)
        self.assertEqual(openrouter_models[0]['id'], 'google/gemini-2.5-flash')

    def test_get_provider_openrouter(self):
        provider = AIProviderFactory.get_provider('google/gemini-2.5-flash')
        self.assertIsInstance(provider, OpenRouterService)

    def test_get_provider_openai(self):
        provider = AIProviderFactory.get_provider('gpt-4o-2024-08-06')
        from Knowmore.services.openai_service import OpenAIService
        self.assertIsInstance(provider, OpenAIService)

    def test_get_provider_claude(self):
        provider = AIProviderFactory.get_provider('claude-3-5-sonnet-latest')
        from Knowmore.services.claude_service import ClaudeService
        self.assertIsInstance(provider, ClaudeService)

class TestOpenRouterService(unittest.IsolatedAsyncioTestCase):
    @patch('Knowmore.services.openrouter_service.AsyncOpenAI')
    async def test_stream_response(self, mock_openai_class):
        # Setup mocks
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_stream = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_stream)
        
        # Mock chunks
        mock_chunk_1 = MagicMock()
        mock_chunk_1.choices = [MagicMock(delta=MagicMock(content="Hello"), finish_reason=None)]
        
        mock_chunk_2 = MagicMock()
        mock_chunk_2.choices = [MagicMock(delta=MagicMock(content=" world"), finish_reason="stop")]
        
        mock_stream.__aiter__.return_value = [mock_chunk_1, mock_chunk_2]
        
        service = OpenRouterService()
        generator = service.stream_response(
            messages=[{"role": "user", "content": "hi"}],
            model="google/gemini-2.5-flash"
        )
        
        chunks = [chunk async for chunk in generator]
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], '0:"Hello"\n')
        self.assertEqual(chunks[1], '0:" world"\n')
        self.assertEqual(chunks[2], 'd:{"finishReason": "stop"}\n')

class TestExaWebSearch(unittest.IsolatedAsyncioTestCase):
    @patch('Knowmore.services.web_search_exa.requests.post')
    async def test_execute_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Exa AI",
                    "url": "https://exa.ai",
                    "text": "Exa is neural search."
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Temporarily ensure API key exists for test
        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            search = ExaWebSearch()
            result = await search.execute(query="test query", limit=3)
            
            self.assertTrue(result["success"])
            self.assertEqual(len(result["results"]), 1)
            self.assertEqual(result["results"][0]["title"], "Exa AI")
            self.assertEqual(result["results"][0]["url"], "https://exa.ai")
            self.assertEqual(result["results"][0]["markdown"], "Exa is neural search.")
            self.assertEqual(result["results"][0]["description"], "Exa is neural search.")
            
            # Verify request payload
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertEqual(kwargs["json"]["query"], "test query")
            self.assertEqual(kwargs["json"]["numResults"], 3)
            self.assertEqual(kwargs["json"]["contents"]["text"]["maxCharacters"], 5000)

class TestSearchOrchestrator(unittest.TestCase):
    def test_search_tool_selection_exa(self):
        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            orchestrator = SearchOrchestrator()
            self.assertIsInstance(orchestrator.search_tool, ExaWebSearch)

    def test_search_tool_selection_firecrawl(self):
        with patch.dict(os.environ, {"EXA_API_KEY": ""}):
            # Set FIRE_CRAWL_API_TOKEN just to be clean
            with patch.dict(os.environ, {"FIRE_CRAWL_API_TOKEN": "test_fc"}):
                orchestrator = SearchOrchestrator()
                from Knowmore.services.web_search_firecrawl import FirecrawlWebSearch
                self.assertIsInstance(orchestrator.search_tool, FirecrawlWebSearch)

if __name__ == '__main__':
    unittest.main()
