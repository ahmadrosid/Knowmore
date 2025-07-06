import json
import asyncio
from datetime import datetime
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
    
    
    async def generate_search_queries(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Generate 3 different web search queries based on user message using LLM"""
        last_message = self._get_last_user_message(messages)
        if not last_message:
            return []
        
        # Get conversation context (last 3-5 messages)
        conversation_context = self._get_conversation_context(messages, max_messages=5)
        
        # Get current date information
        current_date = datetime.now()
        date_context = f"""Current date: {current_date.strftime('%B %d, %Y')}
Current year: {current_date.year}
Current month: {current_date.strftime('%B')}"""
        
        query_messages = [
            {
                "role": "user",
                "content": f"""Generate 3 different web search queries based on the user's latest message within the context of the conversation. 
The queries should approach the topic from different angles or search for different aspects.

{date_context}

Conversation context:
{conversation_context}

Latest user message: {last_message}

Important guidelines:
- Consider the conversation context to understand what the user is really asking about
- If the latest message refers to "it", "this", "that", etc., use the context to understand what is being referenced
- If the user asks about "latest", "recent", "current", or "new" information, include the current year ({current_date.year}) or month in relevant queries
- For time-sensitive topics, add appropriate year or date qualifiers
- For comparisons or updates, consider including the current year
- Only add date/year when it makes the search more relevant

Return ONLY the 3 search queries, one per line, no explanation or numbering:"""
            }
        ]
        
        try:
            response = await self.claude_service.client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=150,
                messages=query_messages
            )
            
            queries_text = response.content[0].text.strip()
            # Split by newlines and clean up
            queries = [q.strip() for q in queries_text.split('\n') if q.strip()]
            
            # Basic validation and limit to 3
            valid_queries = []
            for query in queries[:3]:
                if 5 < len(query) < 100:
                    valid_queries.append(query)
            
            # Log generated search queries
            print("\n" + "="*60)
            print("🔍 GENERATED SEARCH QUERIES:")
            for i, query in enumerate(valid_queries, 1):
                print(f"  {i}. {query}")
            print("="*60 + "\n")
            
            return valid_queries
                
        except Exception as e:
            print(f"Query generation failed: {e}")
        
        return []
    
    async def execute_search(self, query: str) -> Dict[str, Any]:
        """Execute web search and return formatted results"""
        try:
            result = await self.search_tool.execute(
                query=query,
                limit=3,  # Reduced from 5 to 3 since we're doing 3 searches
                scrape_content=True,
                formats=["markdown"]
            )
            
            if result.get("success"):
                search_results = result.get("results", [])
                return {
                    "results": search_results,
                    "filterTags": [],
                    "summary": f"Found {len(search_results)} relevant sources about {query}",
                    "success": True,
                    "query": query
                }
            else:
                return {
                    "results": [],
                    "filterTags": [],
                    "summary": f"Search failed: {result.get('error', 'Unknown error')}",
                    "success": False,
                    "query": query
                }
                
        except Exception as e:
            return {
                "results": [],
                "filterTags": [],
                "summary": f"Search error: {str(e)}",
                "success": False,
                "query": query
            }
    
    async def execute_multiple_searches(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Execute multiple searches concurrently"""
        if not queries:
            return []
        
        print("\n" + "="*60)
        print("🚀 EXECUTING CONCURRENT SEARCHES...")
        print("="*60)
        
        # Create tasks for all queries
        tasks = [self.execute_search(query) for query in queries]
        
        # Execute all searches concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for i, (query, result) in enumerate(zip(queries, results), 1):
            if isinstance(result, dict) and not isinstance(result, Exception):
                valid_results.append(result)
                
                # Log search results
                print(f"\n📊 Search #{i}: '{query}'")
                print(f"   Status: {'✅ Success' if result.get('success') else '❌ Failed'}")
                if result.get('success'):
                    results_count = len(result.get('results', []))
                    print(f"   Results: {results_count} sources found")
                    
                    # Log top 3 results
                    for j, res in enumerate(result.get('results', [])[:3], 1):
                        print(f"\n   Result {j}:")
                        print(f"     Title: {res.get('title', 'N/A')}")
                        print(f"     URL: {res.get('url', 'N/A')}")
                        if res.get('description'):
                            desc = res.get('description', '')[:100] + '...' if len(res.get('description', '')) > 100 else res.get('description', '')
                            print(f"     Preview: {desc}")
                else:
                    print(f"   Error: {result.get('summary', 'Unknown error')}")
            else:
                print(f"\n❌ Search #{i}: '{queries[i-1]}' - Failed with exception: {result}")
        
        print("\n" + "="*60)
        print(f"✨ SEARCH COMPLETE: {len(valid_results)}/{len(queries)} searches successful")
        print("="*60 + "\n")
        
        return valid_results
    
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
    
    def enhance_messages_with_multiple_searches(
        self, 
        messages: List[Dict[str, Any]], 
        search_results_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Inject multiple search results into conversation context"""
        if not search_results_list or not any(sr.get("results") for sr in search_results_list):
            return messages
        
        # Build combined search context
        context_parts = ["Web search results from multiple queries:"]
        
        result_counter = 1
        for search_result in search_results_list:
            if not search_result.get("results"):
                continue
                
            query = search_result.get("query", "Unknown query")
            context_parts.append(f"\n## Search: '{query}'")
            
            for result in search_result["results"][:3]:  # Limit to 3 results per search
                title = result.get("title", "")
                url = result.get("url", "")
                content = result.get("markdown", result.get("description", ""))
                
                context_parts.append(f"\n{result_counter}. {title}")
                context_parts.append(f"   URL: {url}")
                if content:
                    # Limit content length
                    content = content[:300] + "..." if len(content) > 300 else content
                    context_parts.append(f"   Content: {content}")
                
                result_counter += 1
        
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
    
    def _get_conversation_context(self, messages: List[Dict[str, Any]], max_messages: int = 5) -> str:
        """Get recent conversation context for better search query generation"""
        if not messages:
            return ""
        
        # Get the last N messages (excluding system messages)
        recent_messages = []
        for msg in reversed(messages):
            if msg.get('role') in ['user', 'assistant']:
                # Truncate long messages for context
                content = msg.get('content', '')
                if len(content) > 200:
                    content = content[:200] + "..."
                recent_messages.append(f"{msg.get('role').capitalize()}: {content}")
                
                if len(recent_messages) >= max_messages:
                    break
        
        # Reverse to show in chronological order
        recent_messages.reverse()
        
        return "\n".join(recent_messages)
