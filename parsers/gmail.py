import os
import mailbox
from email.utils import parsedate_to_datetime
from datetime import timezone

def get_email_body(message):
    """
    Traverses a MIME email structure to extract only the plain text body,
    ignoring HTML variants and attachments to keep vector embeddings clean.
    """
    body = ""
    
    # Handle multipart emails (e.g., contains both text/plain and text/html)
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            # Target only plain text, explicitly skipping attachments
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    # Decode the payload from base64/quoted-printable
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode('utf-8', errors='ignore')
                except Exception:
                    pass
    else:
        # Handle simple, single-part emails
        if message.get_content_type() == "text/plain":
            try:
                payload = message.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
            except Exception:
                pass
                
    return body.strip()

def parse(extract_dir):
    """
    Scans for .mbox archives and yields standardized dictionaries.
    Includes built-in heuristic filtering to drop marketing and automated emails.
    Expected output: {"platform": str, "timestamp": float, "sender": str, "content": str, "type": str}
    """
    # Automated senders to immediately drop
    junk_senders = ['noreply', 'no-reply', 'newsletter', 'marketing', 'support', 'info@', 'sales@']

    for root, _, files in os.walk(extract_dir):
        for file in files:
            # Google Takeout exports mail as massive .mbox files
            if file.endswith('.mbox'):
                mbox_path = os.path.join(root, file)
                
                print(f"Opening mailbox: {file}... (This may take a while for large files)")
                # mailbox.mbox handles the complex file boundaries automatically
                mbox = mailbox.mbox(mbox_path)

                for message in mbox:
                    sender = message['From']
                    date_str = message['Date']

                    # Skip broken or incomplete headers
                    if not sender or not date_str:
                        continue

                    # --- Noise Filter: Sender Level ---
                    sender_lower = str(sender).lower()
                    if any(junk in sender_lower for junk in junk_senders):
                        continue

                    try:
                        # Convert RFC 2822 email date string to a standard Unix timestamp
                        dt = parsedate_to_datetime(date_str)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        timestamp = dt.timestamp()
                    except (TypeError, ValueError):
                        continue

                    content = get_email_body(message)

                    # --- Noise Filter: Content Level ---
                    # Skip empty emails, image-only emails, or promotional broadcasts
                    if not content or "unsubscribe" in content.lower() or "view in browser" in content.lower():
                        continue

                    yield {
                        "platform": "Gmail",
                        "timestamp": timestamp,
                        "sender": str(sender),
                        "content": content,
                        "type": "email"
                    }