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
    Scans for Facebook message JSONs within valid inbox and e2ee_cutover directories.
    Extracts standard chats while filtering out Marketplace listings at the JSON level.
    """
    # Target only the directories where real conversations live
    valid_roots = ['inbox', 'e2ee_cutover']
    
    for root, dirs, files in os.walk(extract_dir):
        # Normalize the path so it works perfectly on Windows (\) or Mac/Linux (/)
        normalized_root = root.replace('\\', '/').lower()
        
        # If we aren't deep inside an inbox or e2ee_cutover folder, skip it entirely
        if not any(f"/{vr}/" in normalized_root or normalized_root.endswith(f"/{vr}") for vr in valid_roots):
            continue

        for file in files:
            if file.endswith('.json') and file.startswith('message_'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        chat_data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
                
                # --- The JSON-Level Marketplace & Spam Filter ---
                # Meta usually tags the thread type. If it's Marketplace, kill it immediately.
                thread_type = chat_data.get('thread_type', '')
                if thread_type == 'Marketplace' or thread_type == 'Pending':
                    continue
                
                # Grab the thread title just in case it's a group chat, it adds good context
                thread_title = fix_fb_encoding(chat_data.get('title', 'Direct Message'))

                for msg in chat_data.get('messages', []):
                    content = msg.get('content')
                    ts_ms = msg.get('timestamp_ms')
                    sender = msg.get('sender_name', 'Unknown')
                    
                    if content and ts_ms:
                        yield {
                            "platform": "Facebook",
                            "timestamp": ts_ms / 1000.0,
                            "sender": fix_fb_encoding(sender),
                            "content": fix_fb_encoding(content),
                            "type": "message",
                            "thread_context": thread_title
                        }