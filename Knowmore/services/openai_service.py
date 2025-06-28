import json
import environ
from openai import AsyncOpenAI
from .tools.provider_tools import ProviderTools

env = environ.Env(
    OPENAI_API_KEY=str,
)

class OpenAIService:
    """
    OpenAI service for streaming chat completions with tool calling support.
    
    Vercel AI SDK Stream Protocol Identifiers:
    - '0:' - Regular text content from the model
    - 'a:' - Tool execution result (toolCallId, result)
    - 'b:' - Tool call started (toolCallId, toolName)
    - 'c:' - Tool call arguments streaming (toolCallId, argsTextDelta)
    - '9:' - Full tool call invocation (toolCallId, toolName, args)
    - 'd:' - Completion finished (finishReason)
    - '3:' - Error occurred (error)
    
    Note: Set HTTP header 'x-vercel-ai-data-stream: v1' when using this service.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=env("OPENAI_API_KEY"),
        )

    async def stream_response(self, messages, model="gpt-3.5-turbo", enable_web_search=False):
        tools = None
        tool_instances = {}
        
        # Get tools if web search is enabled
        if enable_web_search:
            tool_instances_list = ProviderTools.get_available_tools(model)
            tools = ProviderTools.get_tool_definitions(model)
            
            # Validate tool definitions
            validated_tools = self._validate_tool_definitions(tools)
            if validated_tools != tools:
                tools = validated_tools
            
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
                    # Send complete tool calls for Vercel AI SDK compatibility
                    if choice.finish_reason == "tool_calls":
                        for tool_call_index, tool_data in pending_tool_calls.items():
                            if tool_data["function_name"] and tool_data["arguments"]:
                                try:
                                    args = json.loads(tool_data["arguments"])
                                    yield f'9:{json.dumps({"toolCallId": tool_data["id"], "toolName": tool_data["function_name"], "args": args})}\n'
                                except json.JSONDecodeError:
                                    # Send with empty args if parsing fails
                                    yield f'9:{json.dumps({"toolCallId": tool_data["id"], "toolName": tool_data["function_name"], "args": {}})}\n'
                    
                    # Execute any pending tool calls
                    if choice.finish_reason == "tool_calls":
                        tool_results = []
                        for tool_call_index, tool_data in pending_tool_calls.items():
                            function_name = tool_data["function_name"]
                            if function_name in tool_instances and tool_data["arguments"]:
                                try:
                                    # Parse arguments with specific error handling
                                    try:
                                        args = json.loads(tool_data["arguments"])
                                    except json.JSONDecodeError as e:
                                        raise ValueError(f"Invalid JSON in tool arguments: {str(e)}")
                                    
                                    # Validate tool instance exists
                                    if function_name not in tool_instances:
                                        raise ValueError(f"Tool '{function_name}' not found in available tools")
                                    
                                    tool_instance = tool_instances[function_name]
                                    
                                    # Execute tool with timeout consideration
                                    try:
                                        result = await tool_instance.execute(**args)
                                    except TypeError as e:
                                        raise ValueError(f"Invalid arguments for tool '{function_name}': {str(e)}")
                                    except Exception as e:
                                        raise RuntimeError(f"Tool execution failed for '{function_name}': {str(e)}")
                                    
                                    # Validate result can be serialized
                                    try:
                                        serialized_result = json.dumps(result)
                                    except (TypeError, ValueError) as e:
                                        # Fallback to string representation if result is not JSON serializable
                                        result = {"result": str(result), "warning": "Result was not JSON serializable"}
                                        serialized_result = json.dumps(result)
                                    
                                    # Send tool result
                                    yield f'a:{json.dumps({"toolCallId": tool_data["id"], "result": result})}\n'
                                    
                                    # Prepare for follow-up call
                                    tool_results.append({
                                        "tool_call_id": tool_data["id"],
                                        "role": "tool",
                                        "content": serialized_result,
                                        "function_name": function_name,
                                        "arguments": tool_data["arguments"]
                                    })
                                    
                                except Exception as e:
                                    # Enhanced error reporting with error type and context
                                    error_type = type(e).__name__
                                    error_result = {
                                        "error": str(e),
                                        "error_type": error_type,
                                        "tool_name": function_name,
                                        "timestamp": json.dumps(None)  # Could add actual timestamp if needed
                                    }
                                    
                                    yield f'a:{json.dumps({"toolCallId": tool_data["id"], "result": error_result})}\n'
                                    
                                    # Prepare error for follow-up call
                                    tool_results.append({
                                        "tool_call_id": tool_data["id"],
                                        "role": "tool",
                                        "content": json.dumps(error_result),
                                        "function_name": function_name,
                                        "arguments": tool_data.get("arguments", "{}")
                                    })
                        
                        # Make follow-up call to get model's final response
                        if tool_results:
                            async for follow_up_chunk in self._handle_followup_response(messages, tool_results, model, tools):
                                yield follow_up_chunk
                    
                    yield f'd:{json.dumps({"finishReason": choice.finish_reason})}\n'
        except Exception as e:
            # Send error using 3: identifier
            yield f'3:{json.dumps({"error": str(e)})}\n'
    
    async def _handle_followup_response(self, original_messages, tool_results, model, tools):
        """Handle follow-up response after tool execution"""
        try:
            # Build message history with tool results
            followup_messages = original_messages.copy()
            
            # Add tool call message (reconstructed from the tool execution)
            tool_calls = []
            for tool_result in tool_results:
                tool_calls.append({
                    "id": tool_result["tool_call_id"],
                    "type": "function",
                    "function": {
                        "name": tool_result.get("function_name", "unknown"),
                        "arguments": tool_result.get("arguments", "{}")
                    }
                })
            
            # Add the assistant message with tool calls to maintain conversation flow
            if tool_calls:
                followup_messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": tool_calls
                })
            
            # Add tool results to message history
            for tool_result in tool_results:
                followup_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_result["tool_call_id"],
                    "content": tool_result["content"]
                })
            
            # Make follow-up call to get final response
            # Note: Do not include tools in follow-up to prevent recursive tool calls
            stream_params = {
                "model": model,
                "messages": followup_messages,
                "stream": True,
                "max_tokens": 1024,
            }
            
            follow_up_stream = await self.client.chat.completions.create(**stream_params)
            
            # Stream the follow-up response
            async for chunk in follow_up_stream:
                choice = chunk.choices[0]
                delta = choice.delta
                
                # Only handle text content in follow-up (no more tool calls expected)
                if delta.content is not None:
                    yield f'0:{json.dumps(delta.content)}\n'
                
                # Handle completion
                if choice.finish_reason is not None:
                    break
                    
        except Exception as e:
            yield f'3:{json.dumps({"error": f"Follow-up call failed: {str(e)}"})}\n'
    
    def _validate_tool_definitions(self, tools):
        """Validate tool definitions against OpenAI tool schema"""
        if not tools or not isinstance(tools, list):
            return tools
        
        validated_tools = []
        for tool in tools:
            try:
                # Validate basic structure
                if not isinstance(tool, dict):
                    continue
                
                # Check required fields
                if tool.get("type") != "function":
                    continue
                
                function_def = tool.get("function")
                if not isinstance(function_def, dict):
                    continue
                
                # Validate function definition
                if not function_def.get("name"):
                    continue
                
                # Validate parameters schema if present
                parameters = function_def.get("parameters")
                if parameters is not None:
                    if not isinstance(parameters, dict):
                        # Fix invalid parameters by setting to empty object
                        function_def["parameters"] = {"type": "object", "properties": {}}
                    else:
                        # Ensure parameters has required type field
                        if parameters.get("type") != "object":
                            parameters["type"] = "object"
                        
                        # Ensure properties field exists
                        if "properties" not in parameters:
                            parameters["properties"] = {}
                
                # Ensure description exists (helpful for model)
                if not function_def.get("description"):
                    function_def["description"] = f"Execute {function_def['name']} function"
                
                validated_tools.append(tool)
                
            except Exception as e:
                # Skip invalid tool definitions rather than failing entire request
                continue
        
        return validated_tools
