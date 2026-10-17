import asyncio
import json
from uuid import uuid4

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import Implementation


class ParallelWebSearch:
    """Anonymous Parallel Search MCP, adapted to Knowmore's source format."""

    endpoint = "https://search.parallel.ai/mcp"
    user_agent = "Knowmore/1.0 (+https://github.com/ahmadrosid/Knowmore)"
    timeout = 30

    def __init__(self):
        # One orchestrator handles the related searches for a chat request.
        self.session_id = str(uuid4())

    async def execute(self, **kwargs):
        query = kwargs["query"]
        try:
            response = await asyncio.wait_for(self._search(query), timeout=self.timeout)
            if response.isError:
                error = " ".join(
                    block.text for block in response.content if block.type == "text"
                )
                return {"success": False, "results": [], "error": error or "Parallel search failed"}

            data = response.structuredContent
            if data is None:
                # Older MCP servers may return the JSON only as text content.
                text = next(block.text for block in response.content if block.type == "text")
                data = json.loads(text)
            if not isinstance(data, dict) or not isinstance(data.get("results"), list):
                raise ValueError("Invalid Parallel search response")

            results = []
            for item in data["results"][:kwargs.get("limit", 5)]:
                content = "\n\n".join(item["excerpts"])
                results.append({
                    "title": item.get("title") or item["url"],
                    "url": item["url"],
                    "markdown": content,
                    "description": content[:300],
                })
            return {"success": True, "results": results, "query": query}
        except asyncio.TimeoutError:
            return {"success": False, "results": [], "error": "Parallel search timed out"}
        except Exception as exc:
            return {"success": False, "results": [], "error": f"Parallel search failed: {exc}"}

    async def _search(self, query):
        async with httpx.AsyncClient(
            headers={"User-Agent": self.user_agent}, timeout=self.timeout,
        ) as client:
            async with streamable_http_client(self.endpoint, http_client=client) as (read, write, _):
                async with ClientSession(
                    read, write, client_info=Implementation(name="Knowmore", version="1.0"),
                ) as session:
                    await session.initialize()
                    return await session.call_tool("web_search", {
                        "objective": query,
                        "search_queries": [query],
                        "session_id": self.session_id,
                    })
