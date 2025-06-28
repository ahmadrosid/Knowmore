Here’s a full breakdown of the **AI SDK data stream protocol**, which is used by tools, frontends (like `useChat`), and custom backends—even in non-JS environments:

### 📡 Stream Protocol Overview

When you stream from the backend (e.g., your Python/FastAPI server), you must use the **Data Stream Protocol**. Make sure to set the HTTP header:

```
x-vercel-ai-data-stream: v1
```

Then emit individual lines as follows—each line starts with a **part-type identifier** and JSON payload, terminated by `\n`:

| Part                | Identifier | Purpose                                            |
| ------------------- | ---------- | -------------------------------------------------- |
| Text                | `0:`       | Streamed text fragments (appends to chat)          |
| Reasoning           | `g:`       | The model's internal reasoning                     |
| Redacted reasoning  | `i:`       | Reasoning redacted for UI display                  |
| Reasoning signature | `j:`       | Cryptographic signature                            |
| Source              | `h:`       | Citation to sources or metadata                    |
| File                | `k:`       | Base64-encoded binary data with MIME               |
| Data                | `2:`       | JSON objects appended to `data` array in `useChat` |
| Message annotations | `8:`       | UI metadata annotations                            |
| Error               | `3:`       | Errors during generation or tools                  |
| **Tool call start** | `b:`       | Initiates a streaming tool call                    |
| **Tool call delta** | `c:`       | Deltas of tool arguments during streaming          |
| **Tool call**       | `9:`       | Full tool call invocation                          |
| **Tool result**     | `a:`       | Tool execution result                              |
| Step start          | `f:`       | Used for multi-step flows                          |
| Step finish         | `e:`       | Indicates step completion                          |
| Message finish      | `d:`       | End of entire message                              |

Every part must follow the format:

```
<identifier>:<JSON>\n
```

Example for a tool call:

```
b:{"toolCallId":"call-1","toolName":"myTool"}\n
c:{"toolCallId":"call-1","argsTextDelta":"..."}\n
9:{"toolCallId":"call-1","toolName":"myTool","args":{...}}\n
a:{"toolCallId":"call-1","result":{...}}\n
```

This protocol aligns with the official spec ([sdk.vercel.ai][1], [sdk.vercel.ai][2], [aihero.dev][3], [sdk.vercel.ai][4], [sdk.vercel.ai][5], [reddit.com][6]).

---

### 🔧 Integrating in a Non-JS Backend

Even if your back end is Python, Go, etc., you can implement this protocol by:

1. **Set header**: `x-vercel-ai-data-stream: v1`
2. **Stream part-by-part**: emit lines per the protocol
3. **Leverage SDK front-end**: `useChat({ api: '/your/stream-endpoint' })`

The Vercel AI UI client understands these parts and handles rendering automatically ([reddit.com][7]).

---

### 🧠 How the Frontend Handles It

Using `useChat`, the client:

* Appends text from `0:` parts to the assistant message
* Collects structured data from `2:` into `chat.data`
* Manages tool invocations via `b:`, `9:`, `a:` parts
* Tracks reasoning, files, annotations, etc., automatically

---

References:

[1]: https://sdk.vercel.ai/docs/ai-sdk-ui/stream-protocol?utm_source=chatgpt.com "AI SDK UI: Stream Protocols"
[2]: https://sdk.vercel.ai/docs/ai-sdk-ui/streaming-data?utm_source=chatgpt.com "AI SDK UI: Streaming Custom Data"
[3]: https://www.aihero.dev/streaming-text-with-vercel-ai-sdk?utm_source=chatgpt.com "Streaming Text With Vercel's AI SDK"
[4]: https://sdk.vercel.ai/docs/ai-sdk-core/generating-text?utm_source=chatgpt.com "AI SDK Core: Generating Text"
[5]: https://sdk.vercel.ai/docs/ai-sdk-core/tools-and-tool-calling?utm_source=chatgpt.com "AI SDK Core: Tool Calling"
[6]: https://www.reddit.com/r/nextjs/comments/1dz2vqj?utm_source=chatgpt.com "How to intercept text stream from server action using Vercel AI SDK"
[7]: https://www.reddit.com/r/nextjs/comments/1ibeu6g?utm_source=chatgpt.com "Streaming with the AI SDK from a custom backend API"
