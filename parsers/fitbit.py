import os
import json
from datetime import datetime, timezone

def parse(extract_dir):
    """
    Scans for Fitbit export JSONs and yields standardized physiological tuples.
    Expected output: (unix_timestamp, metric_type, value)
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.json') and any(x in file for x in ['heart_rate', 'steps', 'sleep']):
                file_path = os.path.join(root, file)
                
                # Determine the metric from the filename
                metric_type = 'unknown'
                if 'heart_rate' in file: 
                    metric_type = 'heart_rate_bpm'
                elif 'steps' in file: 
                    metric_type = 'step_count'
                elif 'sleep' in file:
                    metric_type = 'sleep_score'
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception:
                    continue
                    
                for entry in data:
                    try:
                        dt_str = entry.get('dateTime')
                        if not dt_str:
                            continue
                            
                        # Handle Fitbit's inconsistent timestamp strings
                        try:
                            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                        except ValueError:
                            # Fallback for standard "MM/DD/YY HH:MM:SS" format
                            dt = datetime.strptime(dt_str, "%m/%d/%y %H:%M:%S").replace(tzinfo=timezone.utc)
                            
                        val = entry.get('value')
                        
                        # Extract the actual value, handling Fitbit's nested dictionaries
                        if isinstance(val, dict) and 'bpm' in val:
                            final_val = val['bpm']
                        elif isinstance(val, dict):
                            # Dump the dict as a string if we don't know the exact schema (e.g., sleep stages)
                            final_val = str(val) 
                        else:
                            final_val = float(val)
                            
                        yield (dt.timestamp(), metric_type, final_val)
                        
                    except (KeyError, ValueError, TypeError, AttributeError):
                        continue