import os
import json
from anthropic import AsyncAnthropic

class ClaudeService:
    def __init__(self):
        self.client = AsyncAnthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

    def _supports_web_search(self, model):
        """Check if model supports web search"""
        web_search_models = [
            'claude-opus-4-20250514',
            'claude-sonnet-4-20250514', 
            'claude-3-7-sonnet-20250219',
            'claude-3-5-sonnet-latest',
            'claude-3-5-haiku-latest'
        ]
        return model in web_search_models

    def _get_tools_config(self, model, enable_web_search=True):
        """Get tools configuration for the model"""
        tools = []
        
        if enable_web_search and self._supports_web_search(model):
            tools.append({
                "type": "web_search",
                "web_search": {
                    "max_uses": 3
                }
            })
        
        return tools

    async def stream_response(self, messages, model="claude-3-5-sonnet-20240620", enable_web_search=True):
        tools = self._get_tools_config(model, enable_web_search)
        
        stream_params = {
            "max_tokens": 1024,
            "messages": messages,
            "model": model,
        }
        
        # Add tools if available
        if tools:
            stream_params["tools"] = tools
        
        async with self.client.messages.stream(**stream_params) as stream:
            async for event in stream:
                # Handle different event types from Claude's streaming
                if hasattr(event, 'type'):
                    if event.type == 'content_block_delta':
                        if hasattr(event.delta, 'text'):
                            yield f'0:{json.dumps(event.delta.text)}\n'
                    elif event.type == 'content_block_start':
                        # Handle tool use blocks
                        if hasattr(event.content_block, 'type'):
                            if event.content_block.type == 'server_tool_use':
                                yield f'tool_start:{json.dumps({"type": "server_tool_use", "name": event.content_block.name})}\n'
                    elif event.type == 'web_search_tool_result':
                        # Handle web search results
                        yield f'tool_result:{json.dumps({"type": "web_search_result", "content": event.content})}\n'
                else:
                    # Fallback for text content
                    if hasattr(event, 'text'):
                        yield f'0:{json.dumps(event.text)}\n'
