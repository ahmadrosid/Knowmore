import json
import uuid
from ..services.ai_provider import AIProviderFactory
from ..services.search_orchestrator import SearchOrchestrator


async def event_stream(messages, model, enable_web_search=True):
    """Simplified stream handler with SearchOrchestrator"""
    try:
        # Early return for non-search requests
        if not enable_web_search:
            provider = AIProviderFactory.get_provider(model)
            async for chunk in provider.stream_response(messages, model, enable_web_search=False):
                yield chunk
            return
        
        # Initialize search orchestrator
        search_orchestrator = SearchOrchestrator()
        
        # Generate multiple search queries
        search_queries = await search_orchestrator.generate_search_queries(messages)
        
        if search_queries:
            # Generate tool call IDs for each query upfront
            tool_call_ids = [f"search_{uuid.uuid4().hex[:8]}" for _ in search_queries]
            
            # Stream search indicators for each query
            for i, (query, tool_call_id) in enumerate(zip(search_queries, tool_call_ids)):
                # Stream search start indicator
                yield f'b:{json.dumps({"toolCallId": tool_call_id, "toolName": "web_search"})}\n'
                
                # Stream search query and execution indicators
                yield f'c:{json.dumps({"toolCallId": tool_call_id, "argsTextDelta": query})}\n'
                yield f'9:{json.dumps({"toolCallId": tool_call_id, "toolName": "web_search", "args": {"query": query}})}\n'
            
            # Execute all searches concurrently
            search_results_list = await search_orchestrator.execute_multiple_searches(search_queries)
            
            # Stream search results for each search with matching tool call IDs
            for i, (search_results, tool_call_id) in enumerate(zip(search_results_list, tool_call_ids)):
                yield f'a:{json.dumps({"toolCallId": tool_call_id, "result": search_results})}\n'
            
            # Enhance messages with all search contexts
            enhanced_messages = search_orchestrator.enhance_messages_with_multiple_searches(
                messages, search_results_list
            )
        else:
            enhanced_messages = messages
        
        # Stream AI response
        provider = AIProviderFactory.get_provider(model)
        async for chunk in provider.stream_response(enhanced_messages, model, enable_web_search=False):
            yield chunk
            
    except Exception as e:
        # Log the error and stream it
        print(f"Error in event_stream: {str(e)}")
        import traceback
        traceback.print_exc()
        yield f'3:{json.dumps({"error": f"Stream error: {str(e)}"})}\n'




async def error_stream(message):
    """Generate error stream response using Vercel protocol"""
    yield f'3:{json.dumps({"error": message})}\n'