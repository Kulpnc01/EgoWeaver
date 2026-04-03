# EgoWeaver 2.0: Behavioral Context Engine

EgoWeaver is a multimodal data orchestration and analysis engine designed to reconstruct digital identity and behavioral context from disparate data exports. By weaving together messaging transcripts, spatial history, and physiological telemetry, EgoWeaver creates a high-fidelity narrative of a subject's digital life.

## Core Capabilities

- **Multimodal Weaving:** Synchronizes data from Facebook, Gmail, Snapchat, WhatsApp, Phone/SMS, Gemini (AI), and more.
- **Contextual Anchoring:** Automatically attaches the closest known GPS coordinates and biometric data (Heart Rate, Steps) to every event.
- **Dual-Layer Forensic Schema:** Output records distinguish between "Forensic Anchors" (tight 60s window) and "General Context" (loose 1h window), providing a `context_confidence` score for each event.
- **Behavioral State Mapping:** Infers physiological states (e.g., ELEVATED, BASELINE) based on biometric deviations at the moment of interaction.
- **Identity Discovery:** Automatically "learns" new handles, emails, and identifiers for a subject during processing, updating the target profile recursively.
- **Psychological Density Filtering:** Uses heuristic scoring to separate high-signal personal and business records from automated noise and spam.

## Target Use Cases

1. **Digital Twin Construction:** Build long-term RAG (Retrieval-Augmented Generation) memory for personalized AI agents using a user's own historical data.
2. **Forensic Behavioral Analysis:** Analyze a target subject's emotional and physical state during specific interactions for behavioral prediction and profile reading.

## Setup & Usage

### 1. Requirements
- Python 3.10+
- Dependencies: `pip install -r requirements.txt`

### 2. Configuration
- Copy `config.example.json` to `config.json` and set your preferred input/output paths.
- Copy `subject_profile.example.json` to `subject_profile.json` and populate the `identifiers` list with known emails or handles of the target subject.

### 3. Execution
- **GUI Mode:** Run `python gui_launcher.py` for a visual control panel.
- **CLI Mode:** Run `python egoweaver.py` (ensure `config.json` is set).

## Data Schema
Each event is exported as a Markdown file with a rich YAML frontmatter:

```yaml
---
platform: Gmail
sender: "Subject_Alpha"
timestamp: 2026-03-01 14:20:05
subject_match: true
psych_score: 8.50
category: personal
context_confidence: 0.9
behavioral_state: ELEVATED
location:
  lat: 40.7128
  lon: -74.0060
  accuracy: 15
physiology:
  heart_rate: 112.0
---
[[Subject_Alpha]]
Content of the message or interaction...
```

## Security & Privacy
EgoWeaver is designed for local execution. No data is sent to external servers during the weaving process. Users are responsible for ensuring they have the legal right to process the data exports provided to the engine.

---
*Developed for Deep Behavioral Analysis and Identity Reconstruction.*
