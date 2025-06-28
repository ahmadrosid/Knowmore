import os
import json
from anthropic import Anthropic

class ClaudeService:
    def __init__(self):
        self.client = Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

    def stream_response(self, query, model="claude-3-5-sonnet-20240620"):
        for streaming in self.client.messages.create(
            max_tokens=1024,
            messages=[{"role": "user", "content": query}],
            model=model,
            stream=True
        ):
            print('streaming', streaming)
            yield f'0:{json.dumps(streaming.text)}\n'
