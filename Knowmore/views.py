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
        enable_web_search = body.get('enable_web_search', False)

        if not messages:
            return StreamingHttpResponse(error_stream('No messages found'), content_type='text/event-stream', status=400)

        input_messages = format_messages(messages)
        response = StreamingHttpResponse(
            event_stream(input_messages, model, enable_web_search=enable_web_search), 
            content_type='text/event-stream'
        )
        response['x-vercel-ai-data-stream'] = 'v1'
        return response
    except json.JSONDecodeError:
        return StreamingHttpResponse(error_stream('Invalid JSON'), content_type='text/event-stream', status=400)

def get_models(request):
    """Get available models from all providers"""
    models_dict = AIProviderFactory.get_supported_models()
    
    # Transform into a flat list with provider info
    models = []
    for provider, model_list in models_dict.items():
        for model in model_list:
            models.append({
                'id': model['id'],
                'name': model['name'],
                'provider': provider
            })
    
    return JsonResponse({'models': models})


def get_manifest(request):
    """Read Vite manifest to get the correct asset paths"""
    try:
        manifest_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'dist', '.vite', 'manifest.json')
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        return JsonResponse(manifest)
    except FileNotFoundError:
        return JsonResponse({'error': 'Manifest not found. Please build the frontend first.'}, status=404)
