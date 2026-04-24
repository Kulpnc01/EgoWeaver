import os
import csv
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

def parse_csv_time(time_val):
    if not time_val: return None
    time_val = time_val.strip()
    if time_val.replace('.', '', 1).isdigit():
        val = float(time_val)
        return val / 1000.0 if val > 9999999999 else val
    try:
        clean_str = time_val.replace('T', ' ').replace('Z', '')
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        pass
    return None

def parse(extract_dir):
    for root, _, files in os.walk(extract_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            if file.endswith('.xml'):
                try:
                    tree = ET.parse(file_path)
                    xml_root = tree.getroot()
                except ET.ParseError:
                    continue
                    
                for msg in xml_root.findall('sms'):
                    msg_type = msg.get('type')
                    timestamp_str = msg.get('date') or msg.get('time')
                    body = msg.get('body', '').strip()
                    contact = msg.get('contact_name') or msg.get('address', 'Unknown')
                    if not body or not timestamp_str: continue
                    yield {
                        "platform": "SMS",
                        "timestamp": int(timestamp_str) / 1000.0,
                        "sender": "Self" if msg_type == "2" else contact,
                        "content": body,
                        "type": "message"
                    }
                    
                for call in xml_root.findall('call'):
                    call_type = call.get('type') 
                    timestamp_str = call.get('date')
                    duration = int(call.get('duration', 0))
                    contact = call.get('contact_name') or call.get('number', 'Unknown')
                    if not timestamp_str: continue
                    direction = "Outgoing" if call_type == "2" else ("Missed" if call_type in ["3", "5"] else "Incoming")
                    yield {
                        "platform": "Phone",
                        "timestamp": int(timestamp_str) / 1000.0,
                        "sender": contact,
                        "content": f"[{direction} call lasting {duration // 60}m {duration % 60}s]",
                        "type": "call_log"
                    }

            elif file.endswith('.csv'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        if not reader.fieldnames: continue
                        headers = {name.lower().strip(): name for name in reader.fieldnames}
                        col_date = next((headers[h] for h in ['date', 'time', 'timestamp'] if h in headers), None)
                        col_body = next((headers[h] for h in ['body', 'message', 'text', 'content'] if h in headers), None)
                        col_contact = next((headers[h] for h in ['contact', 'number', 'address', 'from', 'to'] if h in headers), None)
                        col_type = next((headers[h] for h in ['type', 'direction', 'status'] if h in headers), None)
                        col_duration = next((headers[h] for h in ['duration', 'length', 'seconds'] if h in headers), None)
                        
                        if not col_date: continue 

                        for row in reader:
                            ts = parse_csv_time(row.get(col_date))
                            if not ts: continue
                                
                            contact = row.get(col_contact, 'Unknown')
                            msg_type = str(row.get(col_type, '')).lower()
                            is_sent = any(word in msg_type for word in ['sent', 'outgoing', 'out'])
                            
                            if col_body and row.get(col_body):
                                body = row[col_body].strip()
                                if body:
                                    yield {
                                        "platform": "SMS",
                                        "timestamp": ts,
                                        "sender": "Self" if is_sent else contact,
                                        "content": body,
                                        "type": "message"
                                    }
                            elif col_duration and row.get(col_duration):
                                try: dur = int(float(row[col_duration]))
                                except ValueError: dur = 0
                                dir_str = "Outgoing" if is_sent else ("Missed" if "missed" in msg_type else "Incoming")
                                yield {
                                    "platform": "Phone",
                                    "timestamp": ts,
                                    "sender": contact,
                                    "content": f"[{dir_str} call lasting {dur // 60}m {dur % 60}s]",
                                    "type": "call_log"
                                }
                except UnicodeDecodeError:
                    continue