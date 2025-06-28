import json
import environ
from anthropic import AsyncAnthropic

env = environ.Env(
    ANTHROPIC_API_KEY=str,
)

class ClaudeService:
    """
    Simplified Claude service for streaming chat completions without tool support.
    
    Vercel AI SDK Stream Protocol Identifiers:
    - '0:' - Regular text content from the model
    - 'd:' - Completion finished (finishReason)
    - '3:' - Error occurred (error)
    """
    
    def __init__(self):
        self.client = AsyncAnthropic(
            api_key=env("ANTHROPIC_API_KEY"),
        )

    async def stream_response(self, messages, model="claude-3-5-sonnet-20240620", enable_web_search=False):
        """Stream chat completion response without tool support"""
        stream_params = {
            "max_tokens": 1024,
            "messages": messages,
            "model": model,
        }
        
        try:
            async with self.client.messages.stream(**stream_params) as stream:
                async for event in stream:
                    # Handle different event types from Claude's streaming
                    if hasattr(event, 'type'):
                        if event.type == 'content_block_delta':
                            if hasattr(event.delta, 'text'):
                                # Stream text using Vercel protocol
                                yield f'0:{json.dumps(event.delta.text)}\n'
                        
                        elif event.type == 'content_block_start':
                            # Handle initial text content
                            if hasattr(event, 'content_block') and hasattr(event.content_block, 'type'):
                                if event.content_block.type == 'text' and hasattr(event.content_block, 'text'):
                                    if event.content_block.text:
                                        yield f'0:{json.dumps(event.content_block.text)}\n'
                        
                        elif event.type == 'message_stop':
                            # Send message finish with d: identifier
                            yield f'd:{json.dumps({"finishReason": "stop"})}\n'
                    
                    else:
                        # Fallback for text content
                        if hasattr(event, 'text'):
                            yield f'0:{json.dumps(event.text)}\n'
        
        except Exception as e:
            # Send error using 3: identifier
            yield f'3:{json.dumps({"error": str(e)})}\n'