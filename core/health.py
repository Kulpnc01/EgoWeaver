import bisect
from datetime import datetime

def build_health_index(parsed_health_data):
    """
    Takes standardized physiological data from various wearable parsers 
    and sorts it into an array optimized for binary search.
    Expects a list of tuples: (unix_timestamp, metric_type, value)
    """
    print(f"Sorting {len(parsed_health_data)} physiological records...")
    # Sort strictly by timestamp
    parsed_health_data.sort(key=lambda x: x[0])
    return parsed_health_data

def get_closest_health_metrics(health_index, target_unix_time, max_delta_seconds=300):
    """
    Uses binary search to find the closest health metrics within a specific time window.
    For example, finding the closest heart rate reading within 5 minutes of a text message.
    """
    if not health_index: return {}
    
    timestamps = [row[0] for row in health_index]
    idx = bisect.bisect_left(timestamps, target_unix_time)
    
    # Define search bounds to gather context around the exact moment
    start_idx = max(0, idx - 10)
    end_idx = min(len(health_index), idx + 10)
    
    metrics_at_time = {}
    
    for i in range(start_idx, end_idx):
        record_time, metric, value = health_index[i]
        
        # Only grab data if it's within our acceptable time window (e.g., 5 minutes)
        if abs(record_time - target_unix_time) <= max_delta_seconds:
            # Keep the closest reading for each metric type (heart rate, stress, etc.)
            if metric not in metrics_at_time:
                metrics_at_time[metric] = value
                
    return metrics_at_time