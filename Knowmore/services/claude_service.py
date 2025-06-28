import os
import json
from anthropic import AsyncAnthropic

class ClaudeService:
    def __init__(self):
        self.client = AsyncAnthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

    async def stream_response(self, query, model="claude-3-5-sonnet-20240620"):
        async with self.client.messages.stream(
            max_tokens=1024,
            messages=[{"role": "user", "content": query}],
            model=model,
        ) as stream:
            async for text in stream.text_stream:
                yield f'0:{json.dumps(text)}\n'
