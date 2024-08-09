import os
import json

from django.http import StreamingHttpResponse
from django.shortcuts import render

from anthropic import AsyncAnthropic

client = AsyncAnthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

async def ask_claude(query):
    try:
        async with client.messages.stream(
                max_tokens=1024,
                messages=[{"role": "user", "content": query}],
                model="claude-3-5-sonnet-20240620",
            ) as stream:
                async for text in stream.text_stream:
                    message = {
                         'content' : text
                    }
                    data = json.dumps(message)
                    yield "data: " + data + "\n\n"
                yield f"data: <END_STREAMING_SSE>\n\n"

    except Exception as e:
        print(f"Error occurred: {e}")
        yield f"data: {e}\n\n"

def index(request):
    return render(request, "index.html")

async def sse_stream(request):
    query = request.GET.get('query')
    return StreamingHttpResponse(ask_claude(query), content_type='text/event-stream')
