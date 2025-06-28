import json
import uuid
from ..services.ai_provider import AIProviderFactory

async def event_stream(messages, model, enable_web_search=True):
    """Handle AI provider streaming and format response chunks"""
    provider = AIProviderFactory.get_provider(model)

    async for chunk in provider.stream_response(messages, model, enable_web_search=enable_web_search):
        yield chunk

async def error_stream(message):
    """Generate error stream response using Vercel protocol"""
    yield f'3:{json.dumps({"error": message})}\n'