# How to use openai tool call in python?

Here’s a detailed guide on how to use the OpenAI Python library to call tools or functions:

---

## 🔧 1. Setup

First, install and configure the OpenAI Python SDK:

```bash
pip install --upgrade openai
```

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

([geeksforgeeks.org][1])

---

## 🧠 2. Define Tools or Functions

You can define JSON schemas describing the tools or functions your model can invoke. For example, a weather function:

```python
tools = [
  {
    "type": "function",
    "function": {
      "name": "get_current_weather",
      "description": "Get the current weather",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {"type": "string", "description": "City name"},
          "format": {"type": "string", "enum": ["celsius","fahrenheit"]}
        },
        "required": ["location","format"]
      }
    }
  }
]
```

([stackoverflow.com][2])

---

## 3. Ask the Model

Pass the tools list into the `client.chat.completions.create` call:

```python
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": "What's the weather in Jakarta?"}],
    tools=tools
)
```

If the model decides to use one of your functions, the response will include a `function_call` object.
([cookbook.openai.com][3])

---

## 4. Execute the Tool

Check if a function call was requested, then invoke it in Python and return the result:

```python
msg = response.choices[0].message

if msg.get("function_call"):
    func_name = msg.function_call.name
    args = json.loads(msg.function_call.arguments)
    if func_name == "get_current_weather":
        # Call your real weather API
        result = get_current_weather(**args)
        messages.append({"role": "function", "name": func_name, "content": json.dumps(result)})

        # Send the result back for final message
        follow_up = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages
        )
        print(follow_up.choices[0].message.content)
```

---

## 🚀 Complete Example Flow

1. Define tools (JSON schemas).
2. Send user prompt + tools → model replies with a function call.
3. Execute the function in your code and append the result.
4. Make a final call to finish the interaction.

---

## ✅ Why It’s Useful

* The model outputs structured JSON for function calls consistently ([datasciencesouth.com][4], [help.openai.com][5], [serpapi.com][6]).
* Ensures safe, reliable schema with `strict: true` and structured output .

---

## 👩‍💻 Code Snippet Example

```python
import os, json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tools = [{ ... }]  # define function schemas here
messages = [{"role": "user", "content": "What's the weather in Jakarta in celsius?"}]

resp = client.chat.completions.create(model="gpt-4.1", messages=messages, tools=tools)
msg = resp.choices[0].message

if msg.get("function_call"):
    func = msg.function_call
    args = json.loads(func.arguments)

    # your custom function
    weather = get_current_weather(**args)

    messages.append({"role": "function", "name": func.name, "content": json.dumps(weather)})
    final = client.chat.completions.create(model="gpt-4.1", messages=messages)
    print(final.choices[0].message.content)
```

That's it! This is how you **define**, **call**, **execute**, and **respond** to tool-like or function-like requests with OpenAI using Python. Let me know if you'd like help wiring it to real APIs or adding more tools!

[1]: https://www.geeksforgeeks.org/data-science/openai-python-api/?utm_source=chatgpt.com "OpenAI Python API - Complete Guide - GeeksforGeeks"
[2]: https://stackoverflow.com/questions/79315600/how-to-call-openai-function-from-python?utm_source=chatgpt.com "How to call OpenAi function from python - Stack Overflow"
[3]: https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models?utm_source=chatgpt.com "How to call functions with chat models - OpenAI"
[4]: https://datasciencesouth.com/blog/openai-functions/?utm_source=chatgpt.com "OpenAI Function Calling in Python - Data Science South"
[5]: https://help.openai.com/en/articles/8555517-function-calling-in-the-openai-api?utm_source=chatgpt.com "Function Calling in the OpenAI API - OpenAI Help Center"
[6]: https://serpapi.com/blog/connect-openai-with-external-apis-with-function-calling/?utm_source=chatgpt.com "Connect OpenAI with external APIs using Function calling"



---

Suggestion


Your implementation of `OpenAIService.stream_response()` is quite solid and **does cover all four major aspects** of tool calling:

---

### ✅ 1. **Define** Tools

```python
tools = ProviderTools.get_tool_definitions(model)
```

You correctly retrieve and pass the tool schema (`tools`) to the OpenAI API using the `tools` param, which fulfills the **"define"** step.

---

### ✅ 2. **Call** Tools

You listen for `tool_calls` in the streamed chunks:

```python
if delta.tool_calls:
```

And yield updates for:

* Function name (`b:`)
* Arguments (`c:`)

This means you are correctly identifying tool call **intents** from the model, i.e., **"call"** step is covered.

---

### ✅ 3. **Execute** Tools

You parse and execute tools when `finish_reason == "tool_calls"`:

```python
result = await tool_instance.execute(**args)
```

Excellent handling of:

* Tool lookup
* Argument parsing
* Async execution
* Exception handling fallback

✔️ This handles the **"execute"** step effectively.

---

### ✅ 4. **Respond**

You stream back tool results like this:

```python
yield f'a:{json.dumps({"toolCallId": tool_data["id"], "result": result})}\n'
```

Which mimics the `function` role in regular OpenAI tool-calling completions. This allows you to **feed the tool output back to the model**, so it can continue responding.

Although you're not showing a follow-up model call here (e.g., sending messages + function result for a second completion), your system seems **frontend-stream focused**, and it’s clear you're **emitting the result**, likely for the frontend or middleware to handle continuation if needed.

---

### 🟡 Suggestions / Improvements

1. **Final follow-up response (optional):**
   If your goal is to complete the model’s full reply (not just return tool results to the UI), you might want to include:

   ```python
   messages.append({
     "role": "function",
     "name": function_name,
     "content": json.dumps(result)
   })
   ```

   Then re-call the model with those messages for the final user-facing output.

2. **Multiple tool call support (partial):**
   You handle multiple `tool_calls` but may want to double-check robustness if GPT returns more than one at once. You use `index`, which is good — just ensure all results yield properly.

3. **Missing validation / schema check:**
   Depending on `ProviderTools`, you may want to validate tool definitions against the JSON schema standard to prevent silent errors from malformed tool specs.

---

### ✅ Verdict: YES

Your code **fully supports:**

* **Tool definition**
* **Model-triggered function call detection**
* **Argument streaming**
* **Tool execution**
* **Tool result response**

You’re doing everything OpenAI's tool-calling API is designed for. It’s a **well-engineered streaming implementation**.

Let me know if you want help adding final follow-up message handling or testing multi-tool parallel execution!
