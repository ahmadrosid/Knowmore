#!/bin/bash

# Test web search with OpenAI model
echo "Testing web search with OpenAI..."
echo "Expected format: <identifier>:<JSON>"
echo "-----------------------------------"

curl -X POST http://localhost:7000/api/stream \
  -H "Content-Type: application/json" \
  -i \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What is the current weather in Jakarta?"
      }
    ],
    "model": "gpt-4o",
    "enable_web_search": true
  }' \
  -N