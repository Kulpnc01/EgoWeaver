# EgoWeaver

A command-line ETL (Extract, Transform, Load) pipeline designed to normalize disparate personal data exports—ranging from social communications and AI interactions to geographical timelines and physiological biometrics—into a unified format optimized for multidimensional Vector Databases and Knowledge Graphs.

## Architecture

EgoWeaver operates on a highly scalable, memory-efficient "Dual-Index" architecture:

1. **The Core Engines (`core/`):** - **Location Index:** Streams massive spatial logs (like Google's `Records.json`) into a highly compressed, sorted memory index using `ijson`.
   - **Physiological Index:** Parses biometric exports (heart rate, sleep, steps) into a parallel chronological index.
   - Both engines use binary search (`bisect`) to execute sub-millisecond cross-referencing.

2. **The Parsers (`parsers/`):** Modular scripts that strip proprietary formatting from raw exports.
   - **Communications:** Facebook (JSON), WhatsApp (.txt), Gmail (.mbox)
   - **AI Interactions:** ChatGPT, Copilot, Gemini/Bard
   - **Health/Wearables:** Google Fit, Fitbit

3. **The Orchestrator (`egoweaver.py`):** Unzips archives, routes data to the correct parser, queries the core engines for context at that exact timestamp, and writes the output.

## Output Format

The pipeline outputs individual Markdown (`.md`) files enriched with multidimensional YAML Frontmatter, natively formatted for ingestion by LangChain, LlamaIndex, or Neo4j.

```yaml
---
type: message
platform: Facebook
sender: Jane Smith
timestamp: 2026-03-14 08:30:00
location:
  latitude: 37.7749
  longitude: -122.4194
  accuracy_meters: 15
physiology:
  heart_rate_bpm: 112
  step_count: 450
---

Are we still on for the hike today?