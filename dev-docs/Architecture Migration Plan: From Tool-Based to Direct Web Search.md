Current Architecture

## Search Flow

- Anthropic: Uses Claude's native web_search_20250305 tool via AnthropicWebSearch
- OpenAI: Uses FirecrawlWebSearch as a tool through complex tool calling mechanism
- Tool Orchestration: OpenAIService.stream_response() handles tool call lifecycle with retry logic
- Streaming: Complex Vercel AI SDK protocol with tool call states (b:, c:, 9:, a:)

## Current Components

- Knowmore/services/tools/search/web_anthropic.py: Anthropic-specific web search tool wrapper
- Knowmore/services/tools/search/web_firecrawl.py: Firecrawl API integration as tool
- Knowmore/services/openai_service.py: Complex tool call streaming with 200+ lines of tool orchestration
- Knowmore/handlers/stream_handler.py: Simple passthrough to provider services

## Proposed Architecture

### New Search Flow

1. Query Extraction: Analyze user message in stream_handler.py to extract search intent
2. Direct Search: Call FirecrawlWebSearch.execute() directly (not as tool)
3. Context Injection: Summarize search results and inject into conversation context
4. Simplified Streaming: Stream AI response with enriched context, no tool complexity

### Key Changes

Stream Handler (Knowmore/handlers/stream_handler.py)

- Role: Orchestrates entire flow instead of simple passthrough
- Responsibilities:
- Extract search queries from user messages
- Execute direct Firecrawl search
- Stream search loading indicators using Vercel AI SDK protocol
- Summarize search results
- Inject search context into messages
- Coordinate with simplified AI providers

### AI Provider Services

- OpenAI Service: Remove 150+ lines of tool call handling logic
- Anthropic Service: Create new simplified service without tool dependencies
- Unified Interface: Both providers receive enriched messages, no tool awareness needed

### Search Integration

- Direct Execution: FirecrawlWebSearch used as service, not tool
- Unified Search: Single search implementation across all providers
- Enhanced Results: Use scrape_content=True for richer context

### Streaming Protocol

**Search Loading Phase**

b:{"toolCallId": "search_123", "toolName": "web_search"}
c:{"toolCallId": "search_123", "argsTextDelta": "extracted search query"}
9:{"toolCallId": "search_123", "toolName": "web_search", "args": {"query": "..."}}

**Search Results Phase**

a:{"toolCallId": "search_123", "result": {
"searchResults": [...],
"filterTags": [...],
"summary": "Found X relevant sources about..."
}}

**AI Response Phase**

0:"AI response with search context..."
d:{"finishReason": "stop"}

### Frontend Integration

Existing Components (No Changes Needed)

- frontend/src/chat/chat-source.tsx: Displays search results in card layout
- frontend/src/components/chat-source-placeholder.tsx: Shimmer loading animation
- Search result interface already matches Firecrawl output format

### UX Flow

1. User asks question → Immediate placeholder shown
2. Search executes → Progress updates
3. Results found → Replace placeholder with actual sources
4. AI processes → Stream response with search context

## TODO List

### 1. Enhanced Stream Handler
- [ ] Update `Knowmore/handlers/stream_handler.py`
- [ ] Add LLM-based query extraction (call LLM to generate search keywords)
- [ ] Add direct Firecrawl search execution
- [ ] Stream search loading indicators using Vercel AI SDK protocol
- [ ] Inject search results into AI context

### 2. Simplify AI Providers
- [ ] Remove tool orchestration from `Knowmore/services/openai_service.py`
- [ ] Simplify `Knowmore/services/claude_service.py` (remove web search tools)
- [ ] Both providers just stream responses, no tool handling

### 3. Error Handling
- [ ] Add search failure fallbacks
- [ ] Add search timeout (10 seconds)
- [ ] Handle API rate limits

### 4. Testing
- [ ] Test end-to-end search flow
- [ ] Test frontend compatibility
- [ ] Performance testing vs current approach

### 5. Cleanup
- [ ] Remove unused tool code
- [ ] Update documentation
