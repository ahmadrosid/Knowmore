import os
import json
from openai import AsyncOpenAI
from .tools.provider_tools import ProviderTools

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    async def stream_response(self, messages, model="gpt-3.5-turbo", enable_web_search=False):
        tools = None
        tool_instances = {}
        
        # Get tools if web search is enabled
        if enable_web_search:
            tool_instances_list = ProviderTools.get_available_tools(model)
            tools = ProviderTools.get_tool_definitions(model)
            # Create a mapping of tool names to instances for execution
            for tool_instance in tool_instances_list:
                tool_instances[tool_instance.name] = tool_instance

        try:
            stream_params = {
                "model": model,
                "messages": messages,
                "stream": True,
                "max_tokens": 1024,
            }
            
            if tools:
                stream_params["tools"] = tools
            
            stream = await self.client.chat.completions.create(**stream_params)
            
            # Track tool calls that need execution
            pending_tool_calls = {}
            tool_calls_completed = set()
            
            async for chunk in stream:
                choice = chunk.choices[0]
                delta = choice.delta
                
                # Handle regular text content
                if delta.content is not None:
                    yield f'0:{json.dumps(delta.content)}\n'
                
                # Handle tool calls
                if delta.tool_calls:
                    for tool_call_delta in delta.tool_calls:
                        # Use index to track tool calls consistently
                        tool_call_index = getattr(tool_call_delta, 'index', 0)
                        
                        # Initialize tool call if new
                        if tool_call_index not in pending_tool_calls:
                            pending_tool_calls[tool_call_index] = {
                                "id": tool_call_delta.id or f"call_{tool_call_index}",
                                "function_name": "",
                                "arguments": "",
                                "started": False
                            }
                            
                        # Get the current tool call data
                        tool_data = pending_tool_calls[tool_call_index]
                        
                        # Update ID if we get it
                        if tool_call_delta.id:
                            tool_data["id"] = tool_call_delta.id
                        
                        # Start tool call if we have the function name
                        if tool_call_delta.function and tool_call_delta.function.name and not tool_data["started"]:
                            tool_data["function_name"] = tool_call_delta.function.name
                            tool_data["started"] = True
                            yield f'b:{json.dumps({"toolCallId": tool_data["id"], "toolName": tool_call_delta.function.name})}\n'
                        
                        # Stream arguments
                        if tool_call_delta.function and tool_call_delta.function.arguments:
                            tool_data["arguments"] += tool_call_delta.function.arguments
                            yield f'c:{json.dumps({"toolCallId": tool_data["id"], "argsTextDelta": tool_call_delta.function.arguments})}\n'
                
                # Check for finish reason or end of tool calls
                if choice.finish_reason is not None:
                    # Skip sending complete tool calls - not needed for frontend compatibility
                    
                    # Execute any pending tool calls
                    if choice.finish_reason == "tool_calls":
                        for tool_call_index, tool_data in pending_tool_calls.items():
                            function_name = tool_data["function_name"]
                            if function_name in tool_instances and tool_data["arguments"]:
                                try:
                                    # Parse arguments
                                    args = json.loads(tool_data["arguments"])
                                    tool_instance = tool_instances[function_name]
                                    
                                    # Execute tool
                                    result = await tool_instance.execute(**args)
                                    
                                    # Send tool result
                                    yield f'a:{json.dumps({"toolCallId": tool_data["id"], "result": result})}\n'
                                    
                                except Exception as e:
                                    yield f'a:{json.dumps({"toolCallId": tool_data["id"], "result": {"error": str(e)}})}\n'
                    
                    yield f'd:{json.dumps({"finishReason": choice.finish_reason})}\n'
        except Exception as e:
            # Send error using 3: identifier
            yield f'3:{json.dumps({"error": str(e)})}\n'
