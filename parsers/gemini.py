import os
import json
from datetime import datetime, timezone

def parse(extract_dir):
    """
    Scans for Gemini (or Bard) My Activity.json exports and yields standardized dictionaries.
    Expected output format: {"platform": str, "timestamp": float, "sender": str, "content": str, "type": str}
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            # Target the specific activity file within Gemini or Bard export folders
            if file == 'My Activity.json' and ('Gemini' in root or 'Bard' in root):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
                    
                for item in data:
                    try:
                        # Google Takeout time format: "2023-10-25T14:30:00.123Z"
                        time_str = item.get('time')
                        if not time_str:
                            continue
                            
                        # Convert to standard Unix time
                        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                        
                        # Extract the user's prompt
                        content = item.get('title', '')
                        
                        # Clean up Google's auto-generated prefixes to keep the vector embedding pure
                        if content.startswith("Said "):
                            content = content[5:]
                        elif content.startswith("Searched for "):
                            content = content[13:]
                            
                        # Skip empty or system-level interactions
                        if not content:
                            continue
                            
                        yield {
                            "platform": "Gemini",
                            "timestamp": dt.timestamp(),
                            "sender": "Self", 
                            "content": content.strip(),
                            "type": "ai_interaction" # Tagged specifically so you can filter AI chats in your graph
                        }
                        
                    except (ValueError, AttributeError):
                        continue