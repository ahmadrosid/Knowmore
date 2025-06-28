import json
import uuid
from ..services.ai_provider import AIProviderFactory

async def event_stream(messages, model, enable_web_search=True):
    """Handle AI provider streaming and format response chunks"""
    provider = AIProviderFactory.get_provider(model)
    message_id = f"msg-{uuid.uuid4().hex[:24]}"

    # Pass web search option to Claude provider
    if hasattr(provider, 'stream_response'):
        if model.startswith('claude'):
            async for chunk in provider.stream_response(messages, model, enable_web_search=enable_web_search):
                yield chunk
        else:
            async for chunk in provider.stream_response(messages, model):
                yield chunk
    else:
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

async def error_stream(message):
    """Generate error stream response"""
    yield f'error: {message}\n'