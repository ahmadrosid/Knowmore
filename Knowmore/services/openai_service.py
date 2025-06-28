import json
import environ
from openai import AsyncOpenAI

env = environ.Env(
    OPENAI_API_KEY=str,
)

class OpenAIService:
    """
    Simplified OpenAI service for streaming chat completions without tool support.
    
    Vercel AI SDK Stream Protocol Identifiers:
    - '0:' - Regular text content from the model
    - 'd:' - Completion finished (finishReason)
    - '3:' - Error occurred (error)
    
    Note: Set HTTP header 'x-vercel-ai-data-stream: v1' when using this service.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=env("OPENAI_API_KEY"),
        )

    async def stream_response(self, messages, model="gpt-3.5-turbo", enable_web_search=False):
        """Stream chat completion response without tool support"""
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