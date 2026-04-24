import os
import mailbox
from email.utils import parsedate_to_datetime

def get_text_body(msg):
    """Recursively digs through complex MIME multipart emails to find the plain text."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # Look strictly for plain text, ignore HTML and attachments
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except Exception:
                    continue
    else:
        if msg.get_content_type() == "text/plain":
            try:
                return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except Exception:
                pass
    return ""

def parse(extract_dir):
    """Scans for .mbox files and extracts plain text email bodies."""
    print(f"  [GMAIL DEBUG] Scanning {extract_dir} for .mbox files...")
    
    for root, _, files in os.walk(extract_dir):
        for file in files:
            if file.lower().endswith('.mbox'):
                mbox_path = os.path.join(root, file)
                print(f"  [GMAIL DEBUG] Found mbox file: {mbox_path}")
                
                try:
                    # Load the mbox file
                    mb = mailbox.mbox(mbox_path)
                    print(f"  [GMAIL DEBUG] Successfully opened mbox. Processing messages...")
                    
                    message_count = 0
                    for message in mb:
                        sender = message['from'] or "Unknown Sender"
                        date_str = message['date']
                        
                        if not date_str:
                            continue
                            
                        # Convert Email Date format to standard Unix timestamp
                        try:
                            dt = parsedate_to_datetime(date_str)
                            ts = dt.timestamp()
                        except Exception:
                            continue
                            
                        # Extract the actual text body
                        content = get_text_body(message).strip()
                        
                        if not content:
                            continue
                            
                        message_count += 1
                        
                        yield {
                            "platform": "Gmail",
                            "timestamp": ts,
                            "sender": sender,
                            "content": content,
                            "type": "message"
                        }
                        
                    print(f"  [GMAIL DEBUG] Successfully yielded {message_count} text emails.")
                    
                except Exception as e:
                    print(f"  [GMAIL DEBUG] CRITICAL ERROR reading mbox: {e}")