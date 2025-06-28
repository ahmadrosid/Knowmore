import asyncio
from django.http import StreamingHttpResponse, JsonResponse

from .services.ai_provider import AIProviderFactory

class SSEResponse(StreamingHttpResponse):
    def __init__(self, streaming_content=(), *args, **kwargs):
        sync_streaming_content = self.get_sync_iterator(streaming_content)
        super().__init__(streaming_content=sync_streaming_content, *args, **kwargs)

    @staticmethod
    async def convert_async_iterable(stream):
        """Accepts async_generator and async_iterator"""
        return [chunk async for chunk in stream]

    def get_sync_iterator(self, async_iterable):
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop running, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.convert_async_iterable(async_iterable))
            loop.close()
            return iter(result)
        else:
            # Event loop is already running, use asyncio.create_task or run_in_executor
            import concurrent.futures
            import threading
            
            def run_async_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result = new_loop.run_until_complete(self.convert_async_iterable(async_iterable))
                    return result
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_in_thread)
                result = future.result()
                return iter(result)
