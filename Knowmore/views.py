import os
import json
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .services.ai_provider import AIProviderFactory
from .utils import get_vite_assets

def index(request):
    assets = get_vite_assets()
    return render(request, "react_app.html", {"assets": assets})

def legacy_index(request):
    return render(request, "index.html")

@csrf_exempt
def sse_stream(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            messages = body.get('messages', [])
            model = body.get('model', 'claude-3-5-sonnet-20240620')
            
            # Extract the last user message
            last_message = ''
            for msg in reversed(messages):
                if msg.get('role') == 'user':
                    last_message = msg.get('content', '')
                    break
            
            if not last_message:
                return JsonResponse({'error': 'No user message found'}, status=400)
            
            provider = AIProviderFactory.get_provider(model)
            
            def ai_sdk_stream():
                import asyncio
                import uuid
                import queue
                import threading
                
                # Generate message ID
                message_id = f"msg-{uuid.uuid4().hex[:24]}"
                
                # Send initial message ID
                yield f'f:{json.dumps({"messageId": message_id})}\n'
                
                # Create a queue to communicate between threads
                q = queue.Queue()
                
                def run_async_generator():
                    # Create new event loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    async def stream_chunks():
                        try:
                            async for chunk in provider.stream_response(last_message, model):
                                # Process chunk immediately and put in queue
                                if chunk.startswith('data: '):
                                    data_str = chunk[6:].strip()
                                    if data_str and data_str != '<END_STREAMING_SSE>':
                                        try:
                                            data = json.loads(data_str)
                                            content = data.get('content', '')
                                            if content:
                                                # Put the processed content directly in queue
                                                q.put(('content', content))
                                        except json.JSONDecodeError:
                                            pass
                        finally:
                            q.put(('end', None))  # Signal completion
                    
                    loop.run_until_complete(stream_chunks())
                    loop.close()
                
                # Start the async generator in a separate thread
                thread = threading.Thread(target=run_async_generator)
                thread.start()
                
                # Stream chunks as they arrive
                try:
                    while True:
                        msg_type, content = q.get(timeout=30)  # 30 second timeout
                        if msg_type == 'end':
                            break
                        elif msg_type == 'content':
                            # Format for AI SDK data stream protocol
                            yield f'0:{json.dumps(content)}\n'
                except queue.Empty:
                    # Timeout occurred
                    pass
                
                # Wait for thread to complete
                thread.join(timeout=1)
                
                # Send e: part before finish
                usage_data = {
                    "finishReason": "stop",
                    "usage": {
                        "promptTokens": 0,
                        "completionTokens": 0
                    },
                    "isContinued": False
                }
                yield f'e:{json.dumps(usage_data)}\n'
                
                # Send finish part with usage info (format: d:{finishReason:...,usage:...})
                finish_data = {
                    "finishReason": "stop",
                    "usage": {
                        "promptTokens": 0,
                        "completionTokens": 0
                    }
                }
                yield f'd:{json.dumps(finish_data)}\n'
            
            response = StreamingHttpResponse(ai_sdk_stream(), content_type='text/event-stream; charset=utf-8')
            response['Cache-Control'] = 'no-cache, no-transform'
            response['X-Accel-Buffering'] = 'no'
            response['x-vercel-ai-data-stream'] = 'v1'
            response['Connection'] = 'keep-alive'
            return response
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_manifest(request):
    """Read Vite manifest to get the correct asset paths"""
    try:
        manifest_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'dist', '.vite', 'manifest.json')
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        return JsonResponse(manifest)
    except FileNotFoundError:
        return JsonResponse({'error': 'Manifest not found. Please build the frontend first.'}, status=404)
