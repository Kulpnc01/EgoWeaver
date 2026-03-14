import os
import argparse
import zipfile
import shutil
from datetime import datetime, timezone

# Import our custom engines and parsers
from core import timeline, health, filter
from parsers import (
    facebook, whatsapp, gmail, 
    gemini, copilot, chatgpt, 
    google_fit, fitbit
)

def extract_archives(input_dir, temp_dir):
    """Unzips all archives in the input folder to a temporary directory."""
    print("Extracting archives...")
    for item in os.listdir(input_dir):
        if item.endswith('.zip'):
            print(f" -> Unzipping {item}...")
            with zipfile.ZipFile(os.path.join(input_dir, item), 'r') as z:
                z.extractall(os.path.join(temp_dir, item.replace('.zip', '')))

def main():
    parser = argparse.ArgumentParser(description="EgoWeaver: Unify digital exports into a multidimensional vector graph.")
    parser.add_argument("--timeline", required=True, help="Path to Google Records.json")
    parser.add_argument("--health", required=True, help="Folder containing raw wearable exports (Fitbit/Google Fit)")
    parser.add_argument("--input", required=True, help="Folder containing .zip communication/AI exports")
    parser.add_argument("--output", required=True, help="Directory to save the final Markdown files")
    
    args = parser.parse_args()

    # 1. Build the Geospatial Engine
    timeline_index = timeline.build_index(args.timeline)
    if not timeline_index:
        print("Fatal Error: Could not build timeline index. Exiting.")
        return

    # 2. Build the Physiological Engine
    print(f"\nScanning '{args.health}' for biometrics...")
    raw_health_data = []
    # We pass the raw health export folders directly to the parsers
    raw_health_data.extend(list(google_fit.parse(args.health)))
    raw_health_data.extend(list(fitbit.parse(args.health)))
    health_index = health.build_health_index(raw_health_data)
    print(f"Health index built with {len(health_index)} physiological data points.")

    # 3. Prepare Directories
    os.makedirs(args.output, exist_ok=True)
    temp_dir = os.path.join(args.input, "_temp_extract")
    os.makedirs(temp_dir, exist_ok=True)

    extract_archives(args.input, temp_dir)

    # 4. Register Communication & AI Parsers
    active_parsers = [
        facebook.parse, 
        whatsapp.parse, 
        gmail.parse, 
        gemini.parse, 
        copilot.parse, 
        chatgpt.parse
    ]
    
# 5. The Weaving Process
    total_files = 0
    skipped_files = 0
    print("\nStarting the weaving process...")
    
    for parse_func in active_parsers:
        print(f"Running {parse_func.__module__.split('.')[-1]} parser...")
        
        for msg in parse_func(temp_dir):
            
            # --- THE NEW FILTER ---
            # Only apply the filter to human messages (keep all AI prompts, as prompts are usually high-signal)
            if msg['type'] == 'message':
                psych_score, is_valuable = filter.evaluate_psych_signal(msg['content'])
                if not is_valuable:
                    skipped_files += 1
                    continue
                # Add the score to the message dictionary so it gets saved in the YAML
                msg['psych_score'] = psych_score
            else:
                msg['psych_score'] = 5.0 # Give AI interactions a default high score
            # ----------------------

            # Fetch Context from Engines
            coord = timeline.get_closest_coordinate(timeline_index, msg['timestamp'])
            physio = health.get_closest_health_metrics(health_index, msg['timestamp'])
            
            # ... (The rest of the writing logic remains exactly the same, 
            # just add `f"  psych_score: {msg['psych_score']}\n"` to your YAML output block)            
            # Format Data
            lat, lon, acc = (coord[1], coord[2], coord[3]) if coord else ("null", "null", "null")
            clean_time = datetime.fromtimestamp(msg['timestamp'], tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            safe_sender = "".join(c for c in msg['sender'] if c.isalnum() or c in (' ', '_'))
            
            filename = f"{msg['platform']}_{safe_sender}_{int(msg['timestamp'])}.md"
            out_path = os.path.join(args.output, filename)
            
            # Write Vector-Ready Markdown
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write("---\n")
                f.write(f"type: {msg.get('type', 'message')}\n")
                f.write(f"platform: {msg['platform']}\n")
                f.write(f"sender: {msg['sender']}\n")
                f.write(f"timestamp: {clean_time}\n")
                f.write(f"psych_score: {msg['psych_score']}\n")
                
                f.write("location:\n")
                f.write(f"  latitude: {lat}\n")
                f.write(f"  longitude: {lon}\n")
                f.write(f"  accuracy_meters: {acc}\n")
                
                f.write("physiology:\n")
                if physio:
                    for metric, value in physio.items():
                        f.write(f"  {metric}: {value}\n")
                else:
                    f.write("  data: null\n")
                    
                f.write("---\n\n")
                f.write(msg['content'])
            
            total_files += 1

    # 6. Cleanup
    print("\nCleaning up temporary files...")
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"\nSuccess! EgoWeaver generated {total_files} multidimensional files in '{args.output}'.")

if __name__ == "__main__":
    main()