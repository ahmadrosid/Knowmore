from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import time

@csrf_exempt
def test_stream(request):
    """Test endpoint to verify streaming works"""
    def generate():
        # Send initial message ID
        yield f'f:{{"messageId":"msg-test123"}}\n'
        
        # Send some test chunks
        test_words = ["Hello", " ", "world", "!", " ", "This", " ", "is", " ", "streaming", "."]
        for i, word in enumerate(test_words):
            yield f'0:{json.dumps(word)}\n'
            time.sleep(0.2)  # Longer delay to see streaming effect
        
        # Send finish messages
        yield f'e:{{"finishReason":"stop","usage":{{"promptTokens":10,"completionTokens":11}},"isContinued":false}}\n'
        yield f'd:{{"finishReason":"stop","usage":{{"promptTokens":10,"completionTokens":11}}}}\n'
    
    response = StreamingHttpResponse(generate(), content_type='text/event-stream; charset=utf-8')
    response['Cache-Control'] = 'no-cache, no-transform'
    response['X-Accel-Buffering'] = 'no'
    response['x-vercel-ai-data-stream'] = 'v1'
    response['Connection'] = 'keep-alive'
    return response

@csrf_exempt 
def simple_stream(request):
    """Very basic SSE test"""
    def generate():
        for i in range(10):
            yield f"data: chunk {i}\n\n"
            time.sleep(0.0010)
        yield "data: [DONE]\n\n"
    
    response = StreamingHttpResponse(generate(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    return response