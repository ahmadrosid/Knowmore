# Testing Web Search UI Integration

## 1. Start the backend server
Make sure your Django backend is running on port 7000

## 2. Start the frontend dev server
```bash
cd frontend
npm run dev
```

## 3. Test queries
Try these queries to test web search:

- "What are the latest AI developments in 2025?"
- "Tell me about the current weather in San Francisco"
- "What's happening with OpenAI today?"

## Expected behavior:

1. When you send a query that triggers web search:
   - You should see the loading placeholder (animated cards)
   - Once results are fetched, you should see the search results in cards
   - The search query should appear as a filter tag

2. The results should display:
   - Title of the webpage
   - URL/domain
   - Preview text
   - Favicon (first letter of domain)

## Debugging tips:

- Open browser console to see any errors
- Check Network tab to verify the streaming response
- Look for events starting with 'b:' (tool start), 'a:' (tool result)