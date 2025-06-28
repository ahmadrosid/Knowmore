import json
from typing import Optional, Dict, Any, List
from .claude_service import ClaudeService
from .web_search_firecrawl import FirecrawlWebSearch


class SearchOrchestrator:
    """
    Orchestrates web search functionality including query extraction and search execution.
    Separates search logic from streaming concerns.
    """
    
    def __init__(self):
        self.claude_service = ClaudeService()
        self.search_tool = FirecrawlWebSearch()
    
    
    async def generate_search_query(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        """Generate web search query based on user message using LLM"""
        last_message = self._get_last_user_message(messages)
        if not last_message:
            return None
        
        query_messages = [
            {
                "role": "user",
                "content": f"""Generate a web search query based on this user message. Return ONLY the search query, no explanation:

User message: {last_message}

Search query:"""
            }
        ]
        
        try:
            response = await self.claude_service.client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=50,
                messages=query_messages
            )
            
            search_query = response.content[0].text.strip()
            
            # Basic validation
            if 5 < len(search_query) < 100:
                return search_query
                
        except Exception as e:
            print(f"Query generation failed: {e}")
        
        return None
    
    async def execute_search(self, query: str) -> Dict[str, Any]:
        """Execute web search and return formatted results"""
        try:
            result = await self.search_tool.execute(
                query=query,
                limit=5,
                scrape_content=True,
                formats=["markdown"]
            )
            
            if result.get("success"):
                search_results = result.get("results", [])
                return {
                    "results": search_results,
                    "filterTags": [],
                    "summary": f"Found {len(search_results)} relevant sources about {query}",
                    "success": True
                }
            else:
                return {
                    "results": [],
                    "filterTags": [],
                    "summary": f"Search failed: {result.get('error', 'Unknown error')}",
                    "success": False
                }
                
        except Exception as e:
            return {
                "results": [],
                "filterTags": [],
                "summary": f"Search error: {str(e)}",
                "success": False
            }
    
    def enhance_messages_with_search(
        self, 
        messages: List[Dict[str, Any]], 
        search_results: Dict[str, Any], 
        query: str
    ) -> List[Dict[str, Any]]:
        """Inject search results into conversation context"""
        if not search_results.get("results"):
            return messages
        
        # Build search context
        context_parts = [f"Search results for '{query}':"]
        
        for i, result in enumerate(search_results["results"][:5]):
            title = result.get("title", "")
            url = result.get("url", "")
            content = result.get("markdown", result.get("description", ""))
            
            context_parts.append(f"\n{i+1}. {title}")
            context_parts.append(f"   URL: {url}")
            if content:
                # Limit content length
                content = content[:500] + "..." if len(content) > 500 else content
                context_parts.append(f"   Content: {content}")
        
        search_context = "\n".join(context_parts)
        
        enhanced_messages = []
        
        # Copy all messages except the last user message
        for i, msg in enumerate(messages[:-1]):
            enhanced_messages.append(msg)
        
        # Get the last user message and enhance it with search context
        last_message = messages[-1]
        enhanced_content = f"{last_message['content']}\n\n---\n{search_context}"
        
        enhanced_messages.append({
            "role": last_message["role"],
            "content": enhanced_content
        })
        
        return enhanced_messages
    
    def _get_last_user_message(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        """Get the last user message content"""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                return msg.get('content', '')
        return None
