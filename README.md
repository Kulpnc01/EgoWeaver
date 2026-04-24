# EgoWeaver 2.0: Digital Twin Engine

---

## 1. CORE ARCHITECTURE

EgoWeaver 2.0 is a high-resolution ETL pipeline designed for Digital Twin creation.

LOCATION ENGINE: Merges Google Semantic paths (15m accuracy), Records.json, Snapchat/Facebook coordinate history, and 2008-era Facebook IP city-anchors.
HEALTH ENGINE: Unifies Fitbit, Google Fit, and Samsung Health CSVs. Includes a Conflict Resolver that averages multi-device heart rate/step data within 1-second windows.
SEARCH OPTIMIZATION: Uses binary search (bisect) for sub-millisecond context lookups.

---

## 2. FILTERING & PSYCH-SIGNALS

The filter.py engine scores content based on 'Psychological Density'.

SCORING: +1.5 for Introspection (I, me, my), +2.0 for Emotional/Cognitive verbs.
MARKETPLACE REJECTION: Discards inquiries like 'is this available' or 'shipping' and financial noise (Venmo, Zelle) if content is under 25 words.
VIP BYPASS: Senders (Mandi, Jackie, Tony) and Safe Keywords (Ego Weaver, Vourdalak) bypass all score thresholds via config.json.

---

## 3. FILESYSTEM & HARVESTING

EgoWeaver uses a 'Harvest' model to hunt for data in _temp_extract and Input subfolders.

INPUT/TIMELINE: Persistent storage for location JSONL records.
INPUT/HEALTH: Persistent storage for unified physiological records.
OUTPUT/: Dynamically creates platform-specific folders (e.g., output/Facebook/).

---

## 4. PERMANENT DIGITAL TWIN

Before termination, the script exports 'lean' records to output/Processed_Context/.

These .jsonl files serve as the platform-agnostic 'source of truth' for the Human Digital Twin Knowledge Graph, independent of the original proprietary exports.

---
