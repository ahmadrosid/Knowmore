import asyncio
import json
import os
import unittest
from unittest.mock import AsyncMock, patch

import httpx
from mcp.types import CallToolResult

from Knowmore.handlers.stream_handler import event_stream
from Knowmore.services.search_orchestrator import SearchOrchestrator
from Knowmore.services.web_search_exa import ExaWebSearch
from Knowmore.services.web_search_firecrawl import FirecrawlWebSearch
from Knowmore.services.web_search_parallel import ParallelWebSearch


SOURCES = {"results": [
    {"title": "Django releases", "url": "https://www.djangoproject.com/download/",
     "excerpts": ["Latest Django release", "Supported versions"]},
    {"title": None, "url": "https://docs.djangoproject.com/", "excerpts": ["Documentation"]},
]}
ASYNC_CLIENT = httpx.AsyncClient


class TestParallelSearch(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # No real credentials, saved .env, or inference requests are needed.
        self.environment = patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test-anthropic", "WEB_SEARCH_PROVIDER": "parallel",
        }, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    async def run_mcp(self, orchestrator, result=None, status=200):
        """Run the real SDK transport/session with an HTTP-level fixture."""
        requests = []

        def handle(request):
            requests.append(request)
            self.assertEqual(str(request.url), ParallelWebSearch.endpoint)
            self.assertEqual(request.headers["User-Agent"], ParallelWebSearch.user_agent)
            self.assertNotIn("Authorization", request.headers)
            message = json.loads(request.content)
            method = message["method"]
            if method.startswith("notifications/"):
                return httpx.Response(202)
            if method == "initialize":
                response = {
                    "protocolVersion": "2025-03-26", "capabilities": {},
                    "serverInfo": {"name": "fixture", "version": "1.0"},
                }
            elif method == "tools/list":
                response = {"tools": [{"name": "web_search", "inputSchema": {"type": "object"}}]}
            elif method == "tools/call":
                self.assertEqual(message["params"]["name"], "web_search")
                arguments = message["params"]["arguments"]
                self.assertEqual(arguments["objective"], "Django supported versions")
                self.assertEqual(arguments["search_queries"], ["Django supported versions"])
                self.assertEqual(arguments["session_id"], orchestrator.search_tool.session_id)
                if status != 200:
                    return httpx.Response(status, text="Service unavailable")
                response = result if result is not None else {"content": [], "structuredContent": SOURCES}
            else:
                self.fail(f"Unexpected MCP method: {method}")
            return httpx.Response(200, json={"jsonrpc": "2.0", "id": message["id"], "result": response})

        def client_factory(**kwargs):
            return ASYNC_CLIENT(**kwargs, transport=httpx.MockTransport(handle))

        with patch("Knowmore.services.web_search_parallel.httpx.AsyncClient", side_effect=client_factory):
            result = await orchestrator.execute_search("Django supported versions")
        self.assertIn("initialize", [json.loads(r.content)["method"] for r in requests])
        self.assertIn("tools/call", [json.loads(r.content)["method"] for r in requests])
        return result

    async def test_selected_provider_to_mcp_and_answer_context(self):
        # Explicit Parallel selection wins even when another provider has credentials.
        with patch.dict(os.environ, {"EXA_API_KEY": "unused", "FIRE_CRAWL_API_TOKEN": "unused"}):
            orchestrator = SearchOrchestrator()
        self.assertIsInstance(orchestrator.search_tool, ParallelWebSearch)
        result = await self.run_mcp(orchestrator)
        self.assertTrue(result["success"])
        self.assertEqual(result["query"], "Django supported versions")
        self.assertEqual(result["results"][0]["markdown"], "Latest Django release\n\nSupported versions")
        self.assertEqual(result["results"][0]["description"], result["results"][0]["markdown"])
        self.assertEqual(result["results"][1]["title"], "https://docs.djangoproject.com/")
        messages = [{"role": "user", "content": "Which Django versions are supported?"}]
        enhanced = orchestrator.enhance_messages_with_multiple_searches(messages, [result])
        self.assertIn("https://www.djangoproject.com/download/", enhanced[-1]["content"])
        self.assertIn("Supported versions", enhanced[-1]["content"])
        self.assertEqual(messages[-1]["content"], "Which Django versions are supported?")

    async def test_text_json_response(self):
        result = await self.run_mcp(SearchOrchestrator(), {
            "content": [{"type": "text", "text": json.dumps(SOURCES)}],
        })
        self.assertTrue(result["success"])
        self.assertEqual(len(result["results"]), 2)

    async def test_tool_error_is_a_failed_search(self):
        result = await self.run_mcp(SearchOrchestrator(), {
            "isError": True, "content": [{"type": "text", "text": "Search temporarily unavailable"}],
        })
        self.assertFalse(result["success"])
        self.assertEqual(result["results"], [])
        self.assertIn("Search temporarily unavailable", result["summary"])

    async def test_http_failure_is_a_failed_search(self):
        result = await self.run_mcp(SearchOrchestrator(), status=503)
        self.assertFalse(result["success"])
        self.assertEqual(result["results"], [])

    async def test_malformed_response_is_a_failed_search(self):
        for response in ({"wrong": []}, {"results": [{"url": "https://example.org"}]}):
            with self.subTest(response=response):
                result = await self.run_mcp(SearchOrchestrator(), {"content": [], "structuredContent": response})
                self.assertFalse(result["success"])
                self.assertEqual(result["results"], [])

    async def test_result_limit_and_empty_results(self):
        provider = ParallelWebSearch()
        with patch.object(provider, "_search", AsyncMock(return_value=CallToolResult(
            content=[], structuredContent=SOURCES,
        ))):
            result = await provider.execute(query="Django releases", limit=1)
        self.assertEqual(len(result["results"]), 1)
        result = await self.run_mcp(SearchOrchestrator(), {"content": [], "structuredContent": {"results": []}})
        self.assertTrue(result["success"])
        self.assertEqual(result["results"], [])

    async def test_timeout_cancels_pending_search(self):
        orchestrator = SearchOrchestrator()
        orchestrator.search_tool.timeout = 0.01
        stopped = asyncio.Event()

        async def slow_search(query):
            try:
                await asyncio.Event().wait()
            finally:
                stopped.set()

        with patch.object(orchestrator.search_tool, "_search", side_effect=slow_search):
            result = await orchestrator.execute_search("Django versions")
        self.assertFalse(result["success"])
        self.assertIn("timed out", result["summary"])
        self.assertTrue(stopped.is_set())

    async def test_cancellation_propagates(self):
        orchestrator = SearchOrchestrator()
        entered = asyncio.Event()
        stopped = asyncio.Event()

        async def slow_search(query):
            try:
                entered.set()
                await asyncio.Event().wait()
            finally:
                stopped.set()

        with patch.object(orchestrator.search_tool, "_search", side_effect=slow_search):
            task = asyncio.create_task(orchestrator.execute_search("Django versions"))
            await entered.wait()
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        self.assertTrue(stopped.is_set())

    def test_existing_selection_is_preserved(self):
        os.environ.pop("WEB_SEARCH_PROVIDER")
        with patch.dict(os.environ, {"EXA_API_KEY": "test-exa"}):
            self.assertIsInstance(SearchOrchestrator().search_tool, ExaWebSearch)
        with patch.dict(os.environ, {"FIRE_CRAWL_API_TOKEN": "test-firecrawl"}):
            self.assertIsInstance(SearchOrchestrator().search_tool, FirecrawlWebSearch)

    async def test_disabled_search_does_not_construct_orchestrator(self):
        provider = AsyncMock()

        async def answer(*args, **kwargs):
            yield '0:"Answer"\n'

        provider.stream_response = answer
        with patch("Knowmore.handlers.stream_handler.SearchOrchestrator") as factory, patch(
            "Knowmore.handlers.stream_handler.AIProviderFactory.get_provider", return_value=provider,
        ):
            chunks = [chunk async for chunk in event_stream(
                [{"role": "user", "content": "Hi"}], "claude-3-5-sonnet-latest", enable_web_search=False,
            )]
        factory.assert_not_called()
        self.assertEqual(chunks, ['0:"Answer"\n'])


if __name__ == "__main__":
    unittest.main()
