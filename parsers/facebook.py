import os
import json

def fix_fb_encoding(text):
    """
    Repairs Facebook's broken UTF-8 encoding in their JSON exports.
    Without this, emojis and special characters render as mojibake.
    """
    try:
        return text.encode('latin1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
        return text

def parse(extract_dir):
    """
    Scans for Facebook message JSONs and yields standardized dictionaries.
    Expected output format: {"platform": str, "timestamp": float, "sender": str, "content": str, "type": str}
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            # Facebook splits long chats into multiple message_1.json, message_2.json files
            if file.endswith('.json') and file.startswith('message_'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        chat_data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
                    
                for msg in chat_data.get('messages', []):
                    # We only want text messages, skip standalone photos/stickers for now
                    content = msg.get('content')
                    ts_ms = msg.get('timestamp_ms')
                    sender = msg.get('sender_name', 'Unknown')
                    
                    if content and ts_ms:
                        yield {
                            "platform": "Facebook",
                            "timestamp": ts_ms / 1000.0, # Convert ms to standard Unix timestamp
                            "sender": fix_fb_encoding(sender),
                            "content": fix_fb_encoding(content),
                            "type": "message"
                        }