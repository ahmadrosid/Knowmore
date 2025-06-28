def format_messages(messages):
    """Format messages to only include role and content (ignore parts)"""
    formatted_messages = []
    for msg in messages:
        if 'parts' in msg:
            # Extract text content from parts
            content = ""
            for part in msg['parts']:
                if isinstance(part, dict) and 'text' in part:
                    content += part['text']
                elif isinstance(part, str):
                    content += part
            formatted_messages.append({
                "role": msg['role'],
                "content": content
            })
        else:
            # Message already in correct format
            formatted_messages.append({
                "role": msg['role'],
                "content": msg.get('content', '')
            })
    return formatted_messages