import os
import json
from datetime import datetime, timezone

def parse(extract_dir):
    """
    Styled after facebook.py to yield daily-grouped Snapchat transcripts.
    Path: {extract_dir}/json/chat_history.json
    """
    # Snapchat typically uses a fixed filename in a 'json' subdirectory
    file_path = os.path.join(extract_dir, 'json', 'chat_history.json')
    
    if not os.path.exists(file_path):
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return

    # Categories to process
    categories = ['Received Saved Chat History', 'Sent Saved Chat History']
    daily_chats = {}

    for category in categories:
        messages = data.get(category, [])
        for msg in messages:
            content = msg.get('Text', '')
            media_type = msg.get('Media Type', 'TEXT')
            
            # If no text, use the media type as the content placeholder
            if not content and media_type != 'TEXT':
                content = f"[{media_type}]"
            
            if not content:
                continue

            # Snapchat format: "2024-03-15 14:30:05 UTC"
            raw_time = msg.get('Created', '')
            try:
                clean_time = raw_time.replace(' UTC', '')
                dt = datetime.strptime(clean_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                ts = dt.timestamp()
                date_str = dt.strftime("%Y-%m-%d")
            except (ValueError, AttributeError):
                continue

            sender = msg.get('From', 'Unknown')

            if date_str not in daily_chats:
                daily_chats[date_str] = {"timestamp": ts, "messages": []}
            
            daily_chats[date_str]['messages'].append({
                "ts": ts,
                "text": f"[{sender}]: {content}"
            })

    # Group, sort, and yield to match facebook.py behavior
    for date_str in sorted(daily_chats.keys()):
        chat_data = daily_chats[date_str]
        
        # Sort internal messages by timestamp since 'Sent' and 'Received' are separate lists
        chat_data['messages'].sort(key=lambda x: x['ts'])
        
        joined_transcript = "\n".join([m['text'] for m in chat_data['messages']])
        
        yield {
            "platform": "Snapchat",
            "timestamp": chat_data['timestamp'],
            "sender": "Snapchat Thread", # Snapchat JSON doesn't group by specific thread ID easily
            "content": joined_transcript,
            "type": "message"
        }