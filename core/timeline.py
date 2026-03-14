import ijson
import bisect
from datetime import datetime

def build_index(records_path):
    """
    Streams Google's Records.json and returns a sorted timeline array.
    Returns a list of tuples: (unix_timestamp, latitude, longitude, accuracy)
    """
    print(f"Building timeline index from '{records_path}'...")
    timeline_data = []
    
    try:
        with open(records_path, 'rb') as f:
            # ijson streams the file so we don't crash the RAM
            locations = ijson.items(f, 'locations.item')
            for loc in locations:
                ts_str = loc.get('timestamp')
                if not ts_str: 
                    continue
                
                try:
                    # Convert Google's ISO 8601 string to standard Unix timestamp
                    clean_str = ts_str.replace('Z', '+00:00')
                    dt = datetime.fromisoformat(clean_str)
                    unix_time = dt.timestamp()
                    
                    # Convert E7 format to standard decimal degrees
                    lat = loc.get('latitudeE7', 0) / 1e7
                    lon = loc.get('longitudeE7', 0) / 1e7
                    acc = loc.get('accuracy', 0)
                    
                    timeline_data.append((unix_time, lat, lon, acc))
                except ValueError:
                    continue
    except FileNotFoundError:
        print(f"Error: Timeline file not found at {records_path}")
        return None
    
    print(f"Extracted {len(timeline_data)} location points. Sorting index...")
    
    # Sort strictly by timestamp so binary search works perfectly
    timeline_data.sort(key=lambda x: x[0])
    return timeline_data

def get_closest_coordinate(timeline_data, target_unix_time, max_delta_seconds=86400):
    """
    Uses binary search to instantly find the nearest GPS ping to the target time.
    max_delta_seconds prevents tagging locations if the data gap is too large (default 24h).
    """
    if not timeline_data: 
        return None
        
    timestamps = [row[0] for row in timeline_data]
    
    # bisect instantly jumps to the correct chronological insertion point
    idx = bisect.bisect_left(timestamps, target_unix_time)
    
    # Handle absolute edge cases (target is before the first or after the last record)
    if idx == 0: 
        closest = timeline_data[0]
    elif idx == len(timeline_data): 
        closest = timeline_data[-1]
    else:
        # Compare the record just before and just after to see which is closer in time
        before = timeline_data[idx - 1]
        after = timeline_data[idx]
        
        if (target_unix_time - before[0]) < (after[0] - target_unix_time):
            closest = before
        else:
            closest = after
            
    # Sanity check: Is this coordinate actually relevant to the timestamp?
    time_difference = abs(closest[0] - target_unix_time)
    if time_difference > max_delta_seconds:
        return None
        
    return closest