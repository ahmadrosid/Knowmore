import json
import uuid
from ..services.ai_provider import AIProviderFactory
from ..services.search_orchestrator import SearchOrchestrator


async def event_stream(messages, model, enable_web_search=True):
    """Simplified stream handler with SearchOrchestrator"""
    # Early return for non-search requests
    if not enable_web_search:
        provider = AIProviderFactory.get_provider(model)
        async for chunk in provider.stream_response(messages, model, enable_web_search=False):
            yield chunk
        return
    
    # Initialize search orchestrator
    search_orchestrator = SearchOrchestrator()
    
    # Generate search query and execute search
    search_query = await search_orchestrator.generate_search_query(messages)
    
    if search_query:
        # Generate tool call ID and stream search indicators
        tool_call_id = f"search_{uuid.uuid4().hex[:8]}"
        async for chunk in _stream_search_indicators(tool_call_id, search_query):
            yield chunk
        
        # Execute search
        search_results = await search_orchestrator.execute_search(search_query)
        
        # Stream search results
        yield f'a:{json.dumps({"toolCallId": tool_call_id, "result": search_results})}\n'
        
        # Enhance messages with search context
        enhanced_messages = search_orchestrator.enhance_messages_with_search(
            messages, search_results, search_query
        )
    else:
        enhanced_messages = messages
    
    # Stream AI response
    provider = AIProviderFactory.get_provider(model)
    async for chunk in provider.stream_response(enhanced_messages, model, enable_web_search=False):
        yield chunk


async def _stream_search_indicators(tool_call_id: str, search_query: str):
    """Stream search loading indicators using Vercel AI SDK protocol"""
    yield f'b:{json.dumps({"toolCallId": tool_call_id, "toolName": "web_search"})}\n'
    yield f'c:{json.dumps({"toolCallId": tool_call_id, "argsTextDelta": search_query})}\n'
    yield f'9:{json.dumps({"toolCallId": tool_call_id, "toolName": "web_search", "args": {"query": search_query}})}\n'


async def error_stream(message):
    """Generate error stream response using Vercel protocol"""
    yield f'3:{json.dumps({"error": message})}\n'