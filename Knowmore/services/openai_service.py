import os
import json
from openai import AsyncOpenAI


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    async def stream_response(self, query, model="gpt-3.5-turbo"):
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": query}],
                stream=True,
                max_tokens=1024,
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    message = {
                        'content': chunk.choices[0].delta.content
                    }
                    data = json.dumps(message)
                    yield "data: " + data + "\n\n"
            
            yield f"data: <END_STREAMING_SSE>\n\n"

        except Exception as e:
            print(f"Error occurred: {e}")
            yield f"data: {e}\n\n"