import os
import json
from openai import AsyncOpenAI


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    async def stream_response(self, messages, model="gpt-3.5-turbo"):
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            max_tokens=1024,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield f'0:{json.dumps(chunk.choices[0].delta.content)}\n'
