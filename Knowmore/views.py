import os
import json
import asyncio
import uuid
import time

from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render

from .services.ai_provider import AIProviderFactory
from .utils import get_vite_assets
from .sse import SSEResponse

def index(request):
    assets = get_vite_assets()
    return render(request, "react_app.html", {"assets": assets})

async def event_stream(messages, model):
    provider = AIProviderFactory.get_provider(model)
    message_id = f"msg-{uuid.uuid4().hex[:24]}"

    async for chunk in provider.stream_response(messages, model):
        yield chunk

    # Add ending chunks
    usage_data = {
        "finishReason": "stop",
        "usage": {
            "promptTokens": 0,
            "completionTokens": 0
        },
        "isContinued": False
    }
    yield f'e:{json.dumps(usage_data)}\n'
    
    finish_data = {
        "finishReason": "stop",
        "usage": {
            "promptTokens": 0,
            "completionTokens": 0
        }
    }
    yield f'd:{json.dumps(finish_data)}\n'

async def sse_stream(request):
    if request.method != 'POST':
        async def error_stream():
            yield f'error: Method not allowed\n'
        return SSEResponse(error_stream(), content_type='text/event-stream', status=405)

    try:
        body = json.loads(request.body)
        messages = body.get('messages', [])
        model = body.get('model', 'claude-3-5-sonnet-20240620')

        if not messages:
            async def error_stream():
                yield f'error: No messages found\n'
            return SSEResponse(error_stream(), content_type='text/event-stream', status=400)

        # Format messages to only include role and content (ignore parts)
        formatted_messages = []
        for msg in messages:
            if 'parts' in msg:
                # Extract text content from parts
                content = ""
                for part in msg['parts']:
                    if isinstance(part, dict) and 'text' in part:
                        content += part['text']
                    elif isinstance(part, str):
                        content += part
                formatted_messages.append({
                    "role": msg['role'],
                    "content": content
                })
            else:
                # Message already in correct format
                formatted_messages.append({
                    "role": msg['role'],
                    "content": msg.get('content', '')
                })
    
        return StreamingHttpResponse(event_stream(formatted_messages, model), content_type='text/event-stream')
    except json.JSONDecodeError:
        async def error_stream():
            yield f'error: Invalid JSON\n'
        return SSEResponse(error_stream(), content_type='text/event-stream', status=400)

def get_manifest(request):
    """Read Vite manifest to get the correct asset paths"""
    try:
        manifest_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'dist', '.vite', 'manifest.json')
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        return JsonResponse(manifest)
    except FileNotFoundError:
        return JsonResponse({'error': 'Manifest not found. Please build the frontend first.'}, status=404)
