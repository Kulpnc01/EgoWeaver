# EgoWeaver

**EgoWeaver** is a local-first, high-performance ETL (Extract, Transform, Load) pipeline designed to ingest a lifetime of digital exports—social communications, AI interactions, geographical timelines, and physiological biometrics—and weave them into a unified multidimensional graph.

The output is perfectly structured for ingestion into **Obsidian** (as an interactive Knowledge Graph) and **AnythingLLM / LanceDB** (as a Retrieval-Augmented Generation vector database).

## 🧠 Core Philosophy

Traditional data scraping pulls everything, filling vector databases with logistical noise ("On my way", "Uber is here", 2FA codes). EgoWeaver utilizes a heuristic **Psychological Filter** to actively score and triage communications, ensuring that only high-signal, emotionally and narratively dense data enters your vector space.

## ⚙️ Key Features

* **The Dual-Index Architecture:**
  * **Geospatial Engine:** Streams massive Google Location datasets into memory using `ijson`. Dynamically supports both legacy cloud exports (`Records.json`) and modern on-device semantic segment exports (`timeline.json`).
  * **Physiological Engine:** Correlates exact timestamps with your heart rate, step count, and sleep data from wearables.
* **The Bouncer (Signal vs. Noise):**
  * Evaluates messages for "Psychological Density" based on length, self-reference (I/me/my), and cognitive/emotional verbs.
  * Actively blocks transactional language, spam, Marketplace haggling, and corporate "no-reply" emails before they are parsed.
* **Obsidian Graph Optimization:** Automatically injects `[[Sender Name]]` wikilinks and `#Platform` tags into the markdown body to instantly generate interactive relationship nodes in Obsidian's Graph View.
* **Portable Configuration:** Decoupled config settings and `.bat` scripts allow you to run the pipeline across different drives and directories without touching the codebase.

## 🔌 Supported Data Sources (Parsers)

**Communications:**

* **Phone Logs:** SMS Texts and Call History (Supports Android XML backups and Carrier CSV exports).

* **Facebook Messenger:** JSON format (Automatically bypasses Marketplace and Message Requests).
* **WhatsApp:** TXT format (Supports both iOS and Android export syntax).
* **Gmail:** MBOX format (Traverses MIME multi-part emails to extract pure text; blocks marketing/newsletters).

**AI Interactions:**

* **ChatGPT:** Flattens complex node-based JSON trees into chronological prompts and responses.

* **Gemini / Copilot:** Parses HTML and JSON chat histories.

**Contextual Engines:**

* **Location:** Google Takeout (`timeline.json` and `Records.json`).

* **Health:** Google Fit and Fitbit (JSON/CSV).

## 🚀 Installation

EgoWeaver is designed to be lightweight, relying almost entirely on Python's robust standard library.

1. Clone the repository:

   ```bash
   git clone [https://github.com/YourUsername/EgoWeaver.git](https://github.com/YourUsername/EgoWeaver.git)
   cd EgoWeaver

Install the single dependency (ijson) used for memory-safe streaming of massive location files:
pip install -r requirements.txt

## 📂 Project Structure

EgoWeaver/
│
├── core/                   # The master engines and filters
│   ├── filter.py           # Psychological density and spam evaluation
│   ├── timeline.py         # Sub-millisecond GPS indexing via binary search
│   └── health.py           # Biometric timeline indexing
│
├── parsers/                # Modular extraction scripts for specific platforms
│   ├── chatgpt.py
│   ├── facebook.py
│   ├── gmail.py
│   ├── phone.py            # (and others...)
│   └──*__init__.py
│
├── egoweaver.py            # The Master Orchestrator
├── config.json             # Dynamic path memory
├── requirements.txt
└── .gitignore

## 🛠️ Usage

EgoWeaver can be executed via standard CLI arguments or through automated .bat files for a seamless desktop experience.

Method 1: The Automated Batch Scripts (Recommended for Windows)
Drop your data into the default timeline/, health/, and input_zips/ folders inside the project directory, then simply double-click:

run_egoweaver.bat: Executes the master pipeline.

set_as_INPUT_folder.bat: Drop this into an external hard drive folder and run it to dynamically tell EgoWeaver where your raw .zip exports live.

set_as_OUTPUT_folder.bat: Drop this into your Obsidian Vault and run it to set it as the master destination.

Method 2: Command Line Overrides
If you prefer the terminal, you can run the tool and override the config.json paths on the fly:

python egoweaver.py \
  --timeline "D:\Backups\timeline.json" \
  --health "D:\Backups\Wearables" \
  --input "D:\Backups\Zips" \
  --output "C:\Users\Username\Documents\Obsidian_Vault\EgoWeaver"

📄 Output Format
EgoWeaver generates individual .md files natively structured for Markdown readers, Vector Databases, and LLMs.

---

type: message
platform: SMS
sender: John Doe
timestamp: 2024-05-12 14:30:22
psych_score: 5.5
location:
  latitude: 37.7749
  longitude: -122.4194
  accuracy_meters: 15
physiology:
  heart_rate_bpm: 88
  step_count: 1200

---

[[John Doe]] | #SMS

I was just thinking about that trip we took to the mountains.
I really feel like I need to get back out to the woods soon, I've been so overwhelmed with the new project and work lately.

## 🧩 Adding New Parsers

EgoWeaver is infinitely extensible. To add support for a new platform (e.g., Discord, Telegram):

Create a new .py file in the parsers/ directory.

Write a parse(extract_dir) generator function that yields a standard dictionary: {"platform", "timestamp", "sender", "content", "type"}.

Register the function inside the active_parsers list in egoweaver.py.
