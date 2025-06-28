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
    for provider, model_ids in models_dict.items():
        for model_id in model_ids:
            # Generate a display name from the model ID
            if model_id.startswith('claude'):
                if 'opus' in model_id:
                    name = 'Claude Opus 4' if '4-20250514' in model_id else 'Claude Opus'
                elif 'sonnet' in model_id:
                    if '4-20250514' in model_id:
                        name = 'Claude Sonnet 4'
                    elif '3-7' in model_id:
                        name = 'Claude Sonnet 3.7'
                    else:
                        name = 'Claude Sonnet 3.5'
                elif 'haiku' in model_id:
                    name = 'Claude Haiku 3.5'
                else:
                    name = model_id
            elif model_id.startswith('gpt'):
                if 'gpt-4o' in model_id:
                    name = 'GPT-4o'
                elif 'gpt-4.1' in model_id:
                    name = 'GPT-4.1'
                else:
                    name = model_id
            elif model_id.startswith('o4'):
                name = 'O4 Mini'
            else:
                name = model_id
                
            models.append({
                'id': model_id,
                'name': name,
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
