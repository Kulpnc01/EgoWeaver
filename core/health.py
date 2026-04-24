import bisect
from parsers import fitbit, google_fit

def build_health_index(extract_dir):
    """
    Scans the extracted directory using Fitbit and Google Fit parsers
    and sorts the results into a searchable index.
    """
    parsed_health_data = []
    
    print(f" -> Scanning for health data in {extract_dir}...")
    
    # Run Fitbit parser
    try:
        parsed_health_data.extend(list(fitbit.parse(extract_dir)))
    except Exception as e:
        print(f"    [!] Fitbit parsing error: {e}")

    # Run Google Fit parser
    try:
        parsed_health_data.extend(list(google_fit.parse(extract_dir)))
    except Exception as e:
        print(f"    [!] Google Fit parsing error: {e}")

    if not parsed_health_data:
        print("    [!] No physiological records found.")
        return []

    print(f" -> Sorting {len(parsed_health_data)} physiological records...")
    parsed_health_data.sort(key=lambda x: x[0])
    return parsed_health_data

def get_closest_health_metrics(health_index, target_unix_time, max_delta_seconds=300):
    """
    Uses binary search to find the closest health metrics within a specific time window.
    """
    if not health_index: return {}
    
    timestamps = [row[0] for row in health_index]
    idx = bisect.bisect_left(timestamps, target_unix_time)
    
    start_idx = max(0, idx - 10)
    end_idx = min(len(health_index), idx + 10)
    
    metrics_at_time = {}
    
    for i in range(start_idx, end_idx):
        record_time, metric, value = health_index[i]
        
        if abs(record_time - target_unix_time) <= max_delta_seconds:
            if metric not in metrics_at_time:
                metrics_at_time[metric] = value
                
    return metrics_at_time