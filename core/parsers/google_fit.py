import os
import json

def parse(extract_dir):
    """
    Scans for Google Fit JSON files and yields standardized physiological tuples.
    Expected output: (unix_timestamp, metric_type, value)
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            # Target the specific files containing physiological data points
            if file.endswith('.json') and 'derived_com.google' in file:
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception:
                    continue
                
                for point in data.get('Data Points', []):
                    try:
                        # Google Fit records time in nanoseconds
                        ts = int(point['endTimeNanos']) / 1e9
                        metric_name = point.get('dataTypeName', 'unknown')
                        
                        # Clean up the metric names for the YAML output
                        clean_metric = metric_name.split('.')[-1]
                        if 'heart_rate' in metric_name: 
                            clean_metric = 'heart_rate_bpm'
                        elif 'step_count' in metric_name: 
                            clean_metric = 'step_count'
                        
                        val_list = point.get('fitValue', [])
                        if not val_list: 
                            continue
                        
                        # Values can be stored as floats (fpVal) or integers (intVal)
                        val = val_list[0].get('fpVal') or val_list[0].get('intVal')
                        
                        if val is not None:
                            yield (ts, clean_metric, val)
                            
                    except (KeyError, ValueError, TypeError):
                        continue