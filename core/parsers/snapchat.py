import os
import json
from datetime import datetime, timezone

def parse(extract_dir):
    """Hunts for chat_history.json recursively to avoid zip-folder nesting issues."""
    for root, _, files in os.walk(extract_dir):
        if 'chat_history.json' in files:
            file_path = os.path.join(root, 'chat_history.json')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                continue

            daily_chats = {}

            # Handle New Format: Dictionary of usernames/threads
            old_categories = ['Received Saved Chat History', 'Sent Saved Chat History']
            is_new_format = isinstance(data, dict) and not any(k in data for k in old_categories)

            if is_new_format:
                for thread_name, messages in data.items():
                    if not isinstance(messages, list): continue
                    for msg in messages:
                        content = msg.get('Content') or msg.get('Text') or ""
                        media_type = msg.get('Media Type', 'TEXT')
                        if not content and media_type != 'TEXT': content = f"[{media_type}]"
                        if not content: continue

                        try:
                            clean_time = msg.get('Created', '').replace(' UTC', '')
                            dt = datetime.strptime(clean_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                            ts = dt.timestamp()
                            date_str = dt.strftime("%Y-%m-%d")
                        except: continue

                        sender = msg.get('From', thread_name)
                        if date_str not in daily_chats:
                            daily_chats[date_str] = {"messages": []}
                        daily_chats[date_str]['messages'].append({
                            "ts": ts, 
                            "sender_raw": sender, 
                            "text_only": content
                        })

            # Handle Old Format: Category-based
            else:
                for category in old_categories:
                    for msg in data.get(category, []):
                        content = msg.get('Text') or msg.get('Content') or ""
                        media_type = msg.get('Media Type', 'TEXT')
                        if not content and media_type != 'TEXT': content = f"[{media_type}]"
                        if not content: continue

                        try:
                            clean_time = msg.get('Created', '').replace(' UTC', '')
                            dt = datetime.strptime(clean_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                            ts = dt.timestamp()
                            date_str = dt.strftime("%Y-%m-%d")
                        except: continue

                        sender = msg.get('From', 'Unknown')
                        if date_str not in daily_chats:
                            daily_chats[date_str] = {"messages": []}
                        daily_chats[date_str]['messages'].append({
                            "ts": ts, 
                            "sender_raw": sender, 
                            "text_only": content
                        })

            # Yield individual messages for better anchoring and discovery
            for date_str in sorted(daily_chats.keys()):
                for msg_item in daily_chats[date_str]['messages']:
                    yield {
                        "platform": "Snapchat",
                        "timestamp": msg_item['ts'],
                        "sender": msg_item['sender_raw'],
                        "content": msg_item['text_only'],
                        "type": "message"
                    }
