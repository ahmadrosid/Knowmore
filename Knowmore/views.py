import os
import json

from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render

from .utils import get_vite_assets
from .handlers.stream_handler import event_stream, error_stream
from .handlers.message_processor import format_messages
from .services.ai_provider import AIProviderFactory

def index(request):
    assets = get_vite_assets()
    return render(request, "react_app.html", {"assets": assets})


async def sse_stream(request):
    if request.method != 'POST':
        return StreamingHttpResponse(error_stream('Method not allowed'), content_type='text/event-stream', status=405)

    try:
        body = json.loads(request.body)
        messages = body.get('messages', [])
        model = body.get('model', 'claude-3-5-sonnet-20240620')

        if not messages:
            return StreamingHttpResponse(error_stream('No messages found'), content_type='text/event-stream', status=400)

        formatted_messages = format_messages(messages)
        return StreamingHttpResponse(event_stream(formatted_messages, model), content_type='text/event-stream')
    except json.JSONDecodeError:
        return StreamingHttpResponse(error_stream('Invalid JSON'), content_type='text/event-stream', status=400)

async def test_tools(request):
    """Test endpoint for experimenting with tools"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        body = json.loads(request.body)
        model = body.get('model', 'claude-3-5-sonnet-20240620')
        query = body.get('query', 'What is the weather today?')
        tool_config = body.get('config', {})
        
        # Get available tools for the model
        available_tools = AIProviderFactory.get_available_tools(model, **tool_config)
        tool_definitions = AIProviderFactory.get_tool_definitions(model, **tool_config)
        
        # Test tool execution (for Firecrawl only, Anthropic is automatic)
        tool_results = []
        if model.startswith('gpt') and available_tools:
            for tool in available_tools:
                if hasattr(tool, 'execute'):
                    try:
                        result = await tool.execute(query=query, limit=3)
                        tool_results.append({
                            'tool': tool.name,
                            'result': result
                        })
                    except Exception as e:
                        tool_results.append({
                            'tool': tool.name,
                            'error': str(e)
                        })
        
        return JsonResponse({
            'success': True,
            'model': model,
            'query': query,
            'available_tools': [tool.name for tool in available_tools],
            'tool_definitions': tool_definitions,
            'tool_results': tool_results,
            'config': tool_config
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_manifest(request):
    """Read Vite manifest to get the correct asset paths"""
    try:
        manifest_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'dist', '.vite', 'manifest.json')
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        return JsonResponse(manifest)
    except FileNotFoundError:
        return JsonResponse({'error': 'Manifest not found. Please build the frontend first.'}, status=404)
