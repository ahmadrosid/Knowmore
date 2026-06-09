import json
import environ
from openai import AsyncOpenAI

env = environ.Env(
    OPENROUTER_API_KEY=str,
)

class OpenRouterService:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=env("OPENROUTER_API_KEY", default=""),
        )

    async def stream_response(self, messages, model, enable_web_search=False):
        """Stream chat completion response from OpenRouter without tool support"""
        try:
            stream_params = {
                "model": model,
                "messages": messages,
                "stream": True,
                "max_tokens": 1024,
            }
            
            stream = await self.client.chat.completions.create(**stream_params)
            
            async for chunk in stream:
                choice = chunk.choices[0]
                delta = choice.delta
                
                # Handle regular text content
                if delta.content is not None:
                    yield f'0:{json.dumps(delta.content)}\n'
                
                # Handle completion
                if choice.finish_reason is not None:
                    yield f'd:{json.dumps({"finishReason": choice.finish_reason})}\n'
                    
        except Exception as e:
            # Send error using 3: identifier
            yield f'3:{json.dumps({"error": str(e)})}\n'
