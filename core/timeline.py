import os
import ijson
import bisect
from datetime import datetime, timezone

def parse_iso_time(time_str):
    """Helper to cleanly convert Google's varied ISO strings to Unix time."""
    try:
        clean_str = time_str.replace('Z', '+00:00')
        return datetime.fromisoformat(clean_str).timestamp()
    except ValueError:
        return None

def build_index_from_extract(extract_dir):
    """
    Automatically locates the location history file within the unzipped 
    Google Takeout structure and builds the index.
    """
    # Common paths for Location History in Google Takeout
    search_paths = [
        os.path.join("Takeout", "Location History", "Records.json"),
        os.path.join("Takeout", "Location History (Timeline)", "Records.json")
    ]

    for rel_path in search_paths:
        full_path = os.path.join(extract_dir, rel_path)
        if os.path.exists(full_path):
            return build_index(full_path)
            
    # If not found in expected paths, do a recursive search for 'Records.json'
    for root, _, files in os.walk(extract_dir):
        if 'Records.json' in files:
            return build_index(os.path.join(root, 'Records.json'))
            
    print(" -> Warning: No Google Location History (Records.json) found.")
    return None

def build_index(records_path):
    """
    Streams Google location data and returns a sorted timeline array.
    """
    print(f"Building timeline index from '{records_path}'...")
    timeline_data = []
    
    try:
        with open(records_path, 'rb') as f:
            locations = ijson.items(f, 'locations.item')
            for loc in locations:
                ts_str = loc.get('timestamp')
                if not ts_str: continue
                
                unix_time = parse_iso_time(ts_str)
                if not unix_time: continue
                
                lat = loc.get('latitudeE7', 0) / 1e7
                lon = loc.get('longitudeE7', 0) / 1e7
                acc = loc.get('accuracy', 0)
                
                timeline_data.append((unix_time, lat, lon, acc))
                
    except Exception as e:
        print(f" -> Error building index: {e}")
        return None
    
    print(f"Extracted {len(timeline_data)} points. Sorting...")
    timeline_data.sort(key=lambda x: x[0])
    return timeline_data

def get_closest_coordinate(timeline_data, target_unix_time, max_delta_seconds=86400):
    """
    Uses binary search to find the nearest GPS ping to the target time.
    """
    if not timeline_data: return None
        
    timestamps = [row[0] for row in timeline_data]
    idx = bisect.bisect_left(timestamps, target_unix_time)
    
    if idx == 0: 
        closest = timeline_data[0]
    elif idx == len(timeline_data): 
        closest = timeline_data[-1]
    else:
        before = timeline_data[idx - 1]
        after = timeline_data[idx]
        closest = before if (target_unix_time - before[0]) < (after[0] - target_unix_time) else after
            
    if abs(closest[0] - target_unix_time) > max_delta_seconds:
        return None
        
    return closest