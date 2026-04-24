import os
import argparse
import zipfile
import shutil
import json
import uuid
from datetime import datetime, timezone

from core import timeline, health, filter
from parsers import (
    facebook, whatsapp, gmail, 
    gemini, copilot, chatgpt, 
    phone, snapchat
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

def load_config():
    defaults = {"timeline": "timeline/timeline.json", "health": "health", "input": "input_zips", "output": "output_md"}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                defaults.update(json.load(f))
        except json.JSONDecodeError: pass
    return defaults

def save_config(config_data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)

def extract_archives(input_dir, temp_dir):
    print("Extracting archives...")
    for item in os.listdir(input_dir):
        if item.endswith('.zip'):
            print(f" -> Unzipping {item}...")
            try:
                with zipfile.ZipFile(os.path.join(input_dir, item), 'r') as z:
                    z.extractall(os.path.join(temp_dir, item.replace('.zip', '')))
            except zipfile.BadZipFile:
                print(f" -> Warning: {item} is corrupted. Skipping.")

def main():
    config = load_config()
    parser = argparse.ArgumentParser(description="EgoWeaver")
    parser.add_argument("--input", default=config['input'])
    parser.add_argument("--output", default=config['output'])
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    # 1. EXTRACTION
    os.makedirs(args.output, exist_ok=True)
    temp_dir = os.path.join(args.input, "_temp_extract")
    os.makedirs(temp_dir, exist_ok=True)
    extract_archives(args.input, temp_dir)

    # 2. PREPARATION (Location & Health)
    print("\n[Phase 1] Building Global Context Indices...")
    timeline_index = timeline.build_index_from_extract(temp_dir)
    health_index = health.build_health_index(temp_dir)

    # 3. WEAVING (Messages)
    print("\n[Phase 2] Starting the weaving process...")
    active_parsers = [facebook.parse, snapchat.parse, gmail.parse, gemini.parse, phone.parse]
    
    target_dirs = [temp_dir]
    for item in os.listdir(args.input):
        full_path = os.path.join(args.input, item)
        if os.path.isdir(full_path) and item != "_temp_extract":
            target_dirs.append(full_path)

    total_files = 0
    for parse_func in active_parsers:
        parser_name = parse_func.__module__.split('.')[-1]
        print(f"Running {parser_name} parser...")
        
        for d in target_dirs:
            for msg in parse_func(d):
                content = msg.get('content', '')
                if not content or not isinstance(content, str): continue 

                # Scoring & Metadata
                psych_score, is_valuable = filter.evaluate_psych_signal(content) if msg.get('type') == 'message' else (5.0, True)
                if not is_valuable: continue
                msg['psych_score'] = psych_score

                # Context Lookup
                coord = timeline.get_closest_coordinate(timeline_index, msg['timestamp'])
                physio = health.get_closest_health_metrics(health_index, msg['timestamp'])
                
                # Save Markdown
                lat, lon, acc = (coord[1], coord[2], coord[3]) if coord else ("null", "null", "null")
                clean_time = datetime.fromtimestamp(msg['timestamp'], tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                safe_sender = "".join(c for c in msg['sender'] if c.isalnum() or c in (' ', '_'))[:50].strip()
                filename = f"{msg['platform']}_{safe_sender}_{int(msg['timestamp'])}_{uuid.uuid4().hex[:6]}.md"
                
                with open(os.path.join(args.output, filename), 'w', encoding='utf-8') as f:
                    f.write(f"---\ntype: {msg.get('type', 'message')}\nplatform: {msg['platform']}\nsender: {msg['sender']}\ntimestamp: {clean_time}\npsych_score: {msg['psych_score']}\nlocation:\n  latitude: {lat}\n  longitude: {lon}\n  accuracy_meters: {acc}\nphysiology:\n")
                    if physio:
                        for m, v in physio.items(): f.write(f"  {m}: {v}\n")
                    else: f.write("  data: null\n")
                    f.write(f"---\n\n[[{msg['sender']}]] | #{msg['platform'].replace(' ', '')}\n\n{msg['content']}")
                
                total_files += 1

    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"\nSuccess! EgoWeaver generated {total_files} files in '{args.output}'.")

if __name__ == "__main__":
    main()