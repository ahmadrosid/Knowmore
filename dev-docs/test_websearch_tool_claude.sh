#!/bin/bash

# Test web search with Claude model
echo "Testing web search with Claude..."
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
    "model": "claude-3-5-sonnet-latest",
    "enable_web_search": true
  }' \
  -N