import os
import json
from anthropic import AsyncAnthropic


class ClaudeService:
    def __init__(self):
        self.client = AsyncAnthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

    async def stream_response(self, query, model="claude-3-5-sonnet-20240620"):
        try:
            async with self.client.messages.stream(
                max_tokens=1024,
                messages=[{"role": "user", "content": query}],
                model=model,
            ) as stream:
                async for text in stream.text_stream:
                    message = {
                        'content': text
                    }
                    data = json.dumps(message)
                    yield "data: " + data + "\n\n"
                yield f"data: <END_STREAMING_SSE>\n\n"

        except Exception as e:
            print(f"Error occurred: {e}")
            yield f"data: {e}\n\n"