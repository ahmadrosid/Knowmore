import os
import json
import uuid
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
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 5
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
        
        try:
            async with self.client.messages.stream(**stream_params) as stream:
                # Track active tool calls
                active_tool_calls = {}
                
                async for event in stream:
                    # Handle different event types from Claude's streaming
                    if hasattr(event, 'type'):
                        if event.type == 'content_block_delta':
                            if hasattr(event.delta, 'text'):
                                # Stream text using Vercel protocol
                                yield f'0:{json.dumps(event.delta.text)}\n'
                            elif hasattr(event.delta, 'partial_json'):
                                # Handle tool input streaming with c: identifier
                                if hasattr(event, 'index') and event.index in active_tool_calls:
                                    tool_call_id = active_tool_calls[event.index]
                                    yield f'c:{json.dumps({"toolCallId": tool_call_id, "argsTextDelta": event.delta.partial_json})}\n'
                        
                        elif event.type == 'content_block_start':
                            # Handle tool use blocks
                            if hasattr(event, 'content_block') and hasattr(event.content_block, 'type'):
                                if event.content_block.type == 'server_tool_use':
                                    # Start tool call with b: identifier
                                    tool_call_id = event.content_block.id
                                    if hasattr(event, 'index'):
                                        active_tool_calls[event.index] = tool_call_id
                                    yield f'b:{json.dumps({"toolCallId": tool_call_id, "toolName": event.content_block.name})}\n'
                                
                                elif event.content_block.type == 'web_search_tool_result':
                                    # Handle web search results as tool result with a: identifier
                                    content_data = []
                                    if hasattr(event.content_block, 'content') and event.content_block.content:
                                        for item in event.content_block.content:
                                            if hasattr(item, 'type') and item.type == 'web_search_result':
                                                content_data.append({
                                                    "type": "web_search_result",
                                                    "url": getattr(item, 'url', ''),
                                                    "title": getattr(item, 'title', ''),
                                                    "encrypted_content": getattr(item, 'encrypted_content', ''),
                                                    "page_age": getattr(item, 'page_age', '')
                                                })
                                            elif hasattr(item, 'type') and item.type == 'web_search_tool_result_error':
                                                content_data.append({
                                                    "type": "web_search_tool_result_error",
                                                    "error_code": getattr(item, 'error_code', 'unknown')
                                                })
                                    
                                    # Send as tool result
                                    yield f'a:{json.dumps({"toolCallId": event.content_block.tool_use_id, "result": content_data})}\n'
                                
                                elif event.content_block.type == 'text' and hasattr(event.content_block, 'text'):
                                    # Initial text content
                                    if event.content_block.text:
                                        yield f'0:{json.dumps(event.content_block.text)}\n'
                        
                        elif event.type == 'content_block_stop':
                            # When tool input is complete, send the full tool call with 9: identifier
                            if hasattr(event, 'index') and event.index in active_tool_calls:
                                # This would contain the full args, but Claude's API doesn't provide it separately
                                # So we rely on the streaming deltas
                                pass
                        
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
