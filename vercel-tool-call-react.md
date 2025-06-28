# Handle vercel ai sdk tool call in the client with react

To handle and render custom UI in the client when a tool call runs using `@ai-sdk/react`, you can use the `useChat` hook’s built-in tooling support—specifically `onToolCall`, `message.parts`, and `addToolResult`.

## Use `useChat` on the client

Import the hook and set up `onToolCall` and `addToolResult` in your React page:

```tsx
'use client';
import { useChat } from '@ai-sdk/react';
import MapComponent from './components/MapComponent';

export default function ChatPage() {
  const {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    addToolResult,
  } = useChat({
    maxSteps: 5,
    onToolCall: async ({ toolCall }) => {
      if (toolCall.toolName === 'showMap') {
        // Use your custom logic to render/display map
        return {
          toolCallId: toolCall.toolCallId,
          result: { mapUrl: `https://maps.example.com?q=${toolCall.args.location}` },
        };
      }
    },
  });

  return (
    <div>
      {messages.map(msg => (
        <div key={msg.id}>
          <strong>{msg.role}:</strong>
          {msg.parts.map((part, i) => {
            if (part.type === 'text') {
              return <div key={i}>{part.text}</div>;
            }
            if (part.type === 'tool-invocation') {
              const invocation = part.toolInvocation;
              const { toolName, state, toolCallId, args, result } = invocation;

              if (toolName === 'showMap') {
                if (state === 'call' || state === 'running') {
                  return <div key={toolCallId}>Loading map for {args.location}…</div>;
                }
                if (state === 'result') {
                  return (
                    <MapComponent
                      key={toolCallId}
                      mapUrl={result.mapUrl}
                    />
                  );
                }
              }
            }
            return null;
          })}
        </div>
      ))}

      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={handleInputChange}
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```

* `onToolCall` runs automatically when a client-side tool is invoked, giving you the chance to fetch data or initiate UI logic.

* `messages[].parts` exposes each message segment, including tool invocation events.
* For `tool-invocation`, inspect `state`:

  * `"call"` → tool is being invoked
  * `"result"` → the tool has returned a value
* Pass the returned result back via `addToolResult` if needed.

---

#### 3. Render custom UI

Define your UI component to render the tool result:

```tsx
type MapProps = { mapUrl: string };

export function MapComponent({ mapUrl }: MapProps) {
  return (
    <iframe
      src={mapUrl}
      width="100%"
      height="300"
      loading="lazy"
    />
  );
}
```

This keeps your logic modular and maintainable.

---

### 📚 Vercel documents

# Chatbot Tool Usage

With `useChat` and `streamText`, you can use tools in your chatbot application.
The AI SDK supports three types of tools in this context:

1. Automatically executed server-side tools
2. Automatically executed client-side tools
3. Tools that require user interaction, such as confirmation dialogs

The flow is as follows:

1. The user enters a message in the chat UI.
2. The message is sent to the API route.
3. In your server side route, the language model generates tool calls during the `streamText` call.
4. All tool calls are forwarded to the client.
5. Server-side tools are executed using their `execute` method and their results are forwarded to the client.
6. Client-side tools that should be automatically executed are handled with the `onToolCall` callback. You can return the tool result from the callback.
7. Client-side tool that require user interactions can be displayed in the UI.
The tool calls and results are available as tool invocation parts in the `parts` property of the last assistant message.
8. When the user interaction is done, `addToolResult` can be used to add the tool result to the chat.
9. When there are tool calls in the last assistant message and all tool results are available, the client sends the updated messages back to the server. This triggers another iteration of this flow.

The tool call and tool executions are integrated into the assistant message as tool invocation parts. A tool invocation is at first a tool call, and then it becomes a tool result when the tool is executed. The tool result contains all information about the tool call as well as the result of the tool execution.

In order to automatically send another request to the server when all tool
calls are server-side, you need to set
`maxSteps` to a value greater
than 1 in the `useChat` options. It is disabled by default for backward
compatibility.

## Example

In this example, we'll use three tools:

- `getWeatherInformation`: An automatically executed server-side tool that returns the weather in a given city.
- `askForConfirmation`: A user-interaction client-side tool that asks the user for confirmation.
- `getLocation`: An automatically executed client-side tool that returns a random city.

### API route

```tsx
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';
import { z } from 'zod';

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'),
    messages,
    tools: {
      // server-side tool with execute function:
      getWeatherInformation: {
        description: 'show the weather in a given city to the user',
        parameters: z.object({ city: z.string() }),
        execute: async ({}: { city: string }) => {
          const weatherOptions = ['sunny', 'cloudy', 'rainy', 'snowy', 'windy'];
          return weatherOptions[
            Math.floor(Math.random() * weatherOptions.length)
          ];
        },
      },
      // client-side tool that starts user interaction:
      askForConfirmation: {
        description: 'Ask the user for confirmation.',
        parameters: z.object({
          message: z.string().describe('The message to ask for confirmation.'),
        }),
      },
      // client-side tool that is automatically executed on the client:
      getLocation: {
        description:
          'Get the user location. Always ask for confirmation before using this tool.',
        parameters: z.object({}),
      },
    },
  });

  return result.toDataStreamResponse();
}
```

### Client-side page

The client-side page uses the `useChat` hook to create a chatbot application with real-time message streaming.
Tool invocations are displayed in the chat UI as tool invocation parts.
Please make sure to render the messages using the `parts` property of the message.

There are three things worth mentioning:

1. The
    `onToolCall` callback is used to handle client-side tools that should be automatically executed. In this example, the `getLocation` tool is a client-side tool that returns a random city.
2. The
    `toolInvocations` property of the last assistant message contains all tool calls and results. The client-side tool `askForConfirmation` is displayed in the UI. It asks the user for confirmation and displays the result once the user confirms or denies the execution. The result is added to the chat using `addToolResult`.
3. The
    `maxSteps` option is set to 5. This enables several tool use iterations between the client and the server.

```tsx
'use client';

import { ToolInvocation } from 'ai';
import { useChat } from '@ai-sdk/react';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit, addToolResult } =
    useChat({
      maxSteps: 5,

      // run client-side tools that are automatically executed:
      async onToolCall({ toolCall }) {
        if (toolCall.toolName === 'getLocation') {
          const cities = [
            'New York',
            'Los Angeles',
            'Chicago',
            'San Francisco',
          ];
          return cities[Math.floor(Math.random() * cities.length)];
        }
      },
    });

  return (
    <>
      {messages?.map(message => (
        <div key={message.id}>
          <strong>{`${message.role}: `}</strong>
          {message.parts.map(part => {
            switch (part.type) {
              // render text parts as simple text:
              case 'text':
                return part.text;

              // for tool invocations, distinguish between the tools and the state:
              case 'tool-invocation': {
                const callId = part.toolInvocation.toolCallId;

                switch (part.toolInvocation.toolName) {
                  case 'askForConfirmation': {
                    switch (part.toolInvocation.state) {
                      case 'call':
                        return (
                          <div key={callId}>
                            {part.toolInvocation.args.message}
                            <div>
                              <button
                                onClick={() =>
                                  addToolResult({
                                    toolCallId: callId,
                                    result: 'Yes, confirmed.',
                                  })
                                }
                              >
                                Yes
                              </button>
                              <button
                                onClick={() =>
                                  addToolResult({
                                    toolCallId: callId,
                                    result: 'No, denied',
                                  })
                                }
                              >
                                No
                              </button>
                            </div>
                          </div>
                        );
                      case 'result':
                        return (
                          <div key={callId}>
                            Location access allowed:{' '}
                            {part.toolInvocation.result}
                          </div>
                        );
                    }
                    break;
                  }

                  case 'getLocation': {
                    switch (part.toolInvocation.state) {
                      case 'call':
                        return <div key={callId}>Getting location...</div>;
                      case 'result':
                        return (
                          <div key={callId}>
                            Location: {part.toolInvocation.result}
                          </div>
                        );
                    }
                    break;
                  }

                  case 'getWeatherInformation': {
                    switch (part.toolInvocation.state) {
                      // example of pre-rendering streaming tool calls:
                      case 'partial-call':
                        return (
                          <pre key={callId}>
                            {JSON.stringify(part.toolInvocation, null, 2)}
                          </pre>
                        );
                      case 'call':
                        return (
                          <div key={callId}>
                            Getting weather information for{' '}
                            {part.toolInvocation.args.city}...
                          </div>
                        );
                      case 'result':
                        return (
                          <div key={callId}>
                            Weather in {part.toolInvocation.args.city}:{' '}
                            {part.toolInvocation.result}
                          </div>
                        );
                    }
                    break;
                  }
                }
              }
            }
          })}
          <br />
        </div>
      ))}

      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} />
      </form>
    </>
  );
}
```

## Tool call streaming

You can stream tool calls while they are being generated by enabling the
`toolCallStreaming` option in `streamText`.

```tsx
export async function POST(req: Request) {
  // ...

  const result = streamText({
    toolCallStreaming: true,
    // ...
  });

  return result.toDataStreamResponse();
}
```

When the flag is enabled, partial tool calls will be streamed as part of the data stream.
They are available through the `useChat` hook.
The tool invocation parts of assistant messages will also contain partial tool calls.
You can use the `state` property of the tool invocation to render the correct UI.

```tsx
export default function Chat() {
  // ...
  return (
    <>
      {messages?.map(message => (
        <div key={message.id}>
          {message.parts.map(part => {
            if (part.type === 'tool-invocation') {
              switch (part.toolInvocation.state) {
                case 'partial-call':
                  return <>render partial tool call</>;
                case 'call':
                  return <>render full tool call</>;
                case 'result':
                  return <>render tool result</>;
              }
            }
          })}
        </div>
      ))}
    </>
  );
}
```

## Step start parts

When you are using multi-step tool calls, the AI SDK will add step start parts to the assistant messages.
If you want to display boundaries between tool invocations, you can use the `step-start` parts as follows:

```tsx
// ...
// where you render the message parts:
message.parts.map((part, index) => {
  switch (part.type) {
    case 'step-start':
      // show step boundaries as horizontal lines:
      return index > 0 ? (
        <div key={index} className="text-gray-500">
          <hr className="my-2 border-gray-300" />
        </div>
      ) : null;
    case 'text':
    // ...
    case 'tool-invocation':
    // ...
  }
});
// ...
```

## Server-side Multi-Step Calls

You can also use multi-step calls on the server-side with `streamText`.
This works when all invoked tools have an `execute` function on the server side.

```tsx
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';
import { z } from 'zod';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'),
    messages,
    tools: {
      getWeatherInformation: {
        description: 'show the weather in a given city to the user',
        parameters: z.object({ city: z.string() }),
        // tool has execute function:
        execute: async ({}: { city: string }) => {
          const weatherOptions = ['sunny', 'cloudy', 'rainy', 'snowy', 'windy'];
          return weatherOptions[
            Math.floor(Math.random() * weatherOptions.length)
          ];
        },
      },
    },
    maxSteps: 5,
  });

  return result.toDataStreamResponse();
}
```

## Errors

Language models can make errors when calling tools. By default, these errors are masked for security reasons, and show up as "An error occurred" in the UI.

To surface the errors, you can use the `getErrorMessage` function when calling `toDataStreamResponse`.

```tsx
export function errorHandler(error: unknown) {
  if (error == null) {
    return 'unknown error';
  }

  if (typeof error === 'string') {
    return error;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return JSON.stringify(error);
}
```

```tsx
const result = streamText({
  // ...
});

return result.toDataStreamResponse({
  getErrorMessage: errorHandler,
});
```

In case you are using `createDataStreamResponse`, you can use the `onError` function when calling `toDataStreamResponse`:

```tsx
const response = createDataStreamResponse({
  // ...
  async execute(dataStream) {
    // ...
  },
  onError: error => `Custom error: ${error.message}`,
});
```
