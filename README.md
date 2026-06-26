# 📘 ALCA — Adaptive Learning Companion Agent
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Agents](https://img.shields.io/badge/AI-Multi--Agent-orange)

*A Multi-Agent, Tool-Driven, Memory-Powered Adaptive Learning System*

---

# 📑 Table of Contents
1. [Overview](#-overview)
2. [Features](#-features)
3. [System Architecture](#-system-architecture)
4. [Project Structure](#-project-structure)
5. [Getting Started](#-getting-started)
6. [Using ALCA](#-using-alca)
   - [Get Topics](#1-get-topics)
   - [Request a Question](#2-request-a-question)
   - [Submit an Answer](#3-submit-an-answer)
   - [Get Memory](#4-get-memory)
   - [Session Management](#5-session-management)
   - [Run Evaluator](#6-run-evaluator)
7. [CLI Demo](#-cli-demo)
8. [Observability & Logging](#-observability--logging)
9. [Gemini Integration](#-gemini-integration)
10. [How It Works Internally](#-how-it-works-internally)
11. [Quick Demonstration Guide](#-quick-demonstration-guide)
12. [Requirement-to-Feature Mapping](#-requirement-to-feature-mapping)
13. [License](#-license)

---

# 📘 Overview
ALCA is a lightweight yet powerful adaptive learning system designed using:
- **Multi-agent architecture**
- **Custom tool integrations**
- **SQLite-backed long-term memory**
- **Detailed observability & logging system**
- **Evaluator for automated quality checks**
- **REST API + CLI-based learner interface**
- **Optional Gemini-powered AI explanations**

ALCA dynamically diagnoses a learner's understanding, selects the right explanation difficulty, generates adaptive practice questions, and updates memory for personalized learning.

---

# 🚀 Features
| Capability | Description |
|-----------|-------------|
| **Multi-Agent System** | Assessment, Explanation, Practice, and Feedback agents managed by an Orchestrator. |
| **Custom Tools** | Code execution tools, search utilities, and evaluation helpers. |
| **Memory System** | SQLite-based persistent accuracy tracking and session storage. |
| **Observability** | Rotating logs for API, agents, evaluation, and performance timing. |
| **Evaluator Module** | Measures correctness, latency, and topic coverage. |
| **Gemini Integration** | Optional AI-powered enhanced explanations. |
| **REST API** | Endpoints for learning, memory, evaluation, and sessions. |
| **CLI Tutor Mode** | Interactive question–explanation–practice cycle. |

---

# 🧠 System Architecture
```
┌────────────────────────────────────────────────────────────────┐
│                         ALCA System                            │
│                                                                │
│    ┌─────────────────────┐     ┌───────────────────────────┐   │
│    │   REST API (Flask)  │     │    CLI Interface          │   │
│    │  /api/learn         │     │    (demo_cli.py)          │   │
│    │  /api/memory        │     └───────────────────────────┘   │
│    │  /api/topics        │                  │                  │
│    │  /api/evaluate      │                  │                  │
│    └─────────────────────┘                  │                  │
│                │                            │                  │
│                └──────────────┬─────────────┘                  │
│                               │                                │
│                  ┌────────────▼────────────┐                   │
│                  │     LearningSystem      │                   │
│                  │       (main.py)         │                   │
│                  └────────────┬────────────┘                   │
│                               │                                │
│                  ┌────────────▼────────────┐                   │
│                  │      Orchestrator       │  ◄── coordinates  │
│                  │      (agents.py)        │      all agents   │
│                  └──┬──────┬──────┬────┬───┘                   │
│                     │      │      │    │                       │
│          ┌──────────┘  ┌───┘  ┌───┘   ┌┘                       │
│          ▼             ▼      ▼       ▼                        │
│  ┌─────────────┐ ┌───────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ Assessment  │ │Explanation│ │ Practice │ │  Feedback    │   │
│  │   Agent     │ │  Agent    │ │  Agent   │ │    Agent     │   │
│  │(Diagnostic  │ │(topic +   │ │(Adaptive │ │ (Grading +   │   │
│  │ Questions)  │ │difficulty)│ │   Qs)    │ │  Memory Upd) │   │
│  └─────────────┘ └────┬──────┘ └──────────┘ └──────┬───────┘   │
│                       │                            │           │
│              ┌────────▼──────────┐                 │           │
│              │  GeminiExplanation│                 │           │
│              │     Agent (LLM)   │                 │           │
│              │  (w/ fallback)    │                 │           │
│              └───────────────────┘                 │           │
│                                                    │           │
│                              ┌─────────────────────▼─────────┐ │
│                              │       MemoryManager           │ │
│                              │    (SQLite / memory.db)       │ │
│                              │  ┌──────────────────────────┐ │ │
│                              │  │ user_stats (accuracy)    │ │ │
│                              │  │ history (per attempt)    │ │ │
│                              │  └──────────────────────────┘ │ │
│                              └───────────────────────────────┘ │
│                                      ▲                         │
│                                      │  (read for difficulty   │
│                                      └── selection by          │
│                                          Orchestrator)         │
└────────────────────────────────────────────────────────────────┘
```

---

# 📂 Project Structure
```
ALCA/
├── main.py                     # Flask API + Logging + Sessions
├── agents.py                   # Multi-agent system + Gemini agent
├── memory.py                   # SQLite memory manager
├── tools.py                    # Custom tools
├── gemini_tool.py              # Gemini LLM wrapper
├── evaluator.py                # Auto evaluator
├── demo_cli.py                 # Interactive CLI
├── sample_content_expanded.json
├── sample_content.json
├── logs/                       # Auto-generated logs
├── sessions/                   # Stored session data
└── requirements.txt
```

---

# 🏃 Getting Started
### Install dependencies
```
pip install -r requirements.txt
```
### Run the server
```
python main.py
```
Access ALCA at:
```
http://127.0.0.1:8000
```

---

# 🖥 Using ALCA
## 1. Get Topics
```
GET /api/topics
```
Example:
```json
{
    "topics": [
        {"name": "stacks", "has_explanations": true, "has_practice": true},
        {"name": "queues", "has_explanations": true, "has_practice": true}
    ]
}
```

## 2. Request a Question
```json
POST /api/learn
{
  "user_id": "u1",
  "topic": "stacks",
  "answer": ""
}
```

## 3. Submit an Answer
```json
POST /api/learn
{
  "user_id": "u1",
  "topic": "stacks",
  "answer": "LIFO"
}
```

## 4. Get Memory
```
GET /api/memory/u1
```

## 5. Session Management
Store:
```json
POST /api/session/store
{"user_id":"u1", "payload":{"last_topic":"stacks"}}
```
Retrieve:
```
GET /api/session/u1
```

## 6. Run Evaluator
```
python evaluator.py sample_content_expanded.json
```
Outputs `evaluation_report.json`.

---

# 🧪 CLI Demo
```
python demo_cli.py
```
Experience the full cycle:
- Diagnostic
- Explanation
- Practice
- Grading
- Summary

---

# 📊 Observability & Logging
Logs created under `/logs`:
- `app.log` — server startup
- `agents.log` — every agent call
- `api_learn.log` — learning mode requests
- `api_memory.log` — memory interactions
- `api_evaluate.log` — evaluator API
- `evaluator.log` — scoring + timing

Each request logs:
- timestamp
- user\_id
- topic
- agent used
- response time

---

# 🤖 Gemini Integration
ALCA offers optional **Gemini-powered explanations**, enhancing clarity and personalization.

### Workflow:
1. Base explanation fetched from dataset
2. Passed to `GeminiExplanationAgent`
3. Gemini generates a more natural explanation
4. If Gemini fails → fallback explanation returned

### Environment variable:
```
GEMINI_API_KEY=your_key_here
```
This remains **local only** (never committed to Git).

---

# 🧩 Requirement-to-Feature Mapping
| Requirement | Implementation |
|------------|----------------|
| Multi-Agent System | Assessment, Explanation, Practice, Feedback Agents + Orchestrator |
| Tools | Code executor, search utility, evaluator tools |
| Sessions & Memory | SQLite + session snapshots |
| Observability | Rotating logs + timing decorators |
| Evaluation | evaluator.py auto testing framework |
| Gemini (Bonus) | Optional LLM explanation agent |

---

# 🧩 How It Works Internally (High-Level)

ALCA operates through a clean, modular execution pipeline:

1. **User Request** → `/api/learn` or CLI input
2. **Orchestrator Activated** → Chooses which agent to run (diagnostic, explanation, practice, feedback)
3. **Agent Processing** → Generates question, explanation, or grades answer
4. **MemoryManager Update** → Stores attempts, correctness, and history in SQLite
5. **Session Logging** → Saves lightweight JSON session snapshot
6. **Observability Layer** → Logs API timing, agent calls, evaluator output
7. **Response Sent** → Adaptive explanation + stats returned to user

This modular pipeline ensures the system is:

- **Stable** (each module isolated)
- **Explainable** (logs + clear agent roles)
- **Adaptive** (difficulty based on user accuracy)
- **Extensible** (easy to add new agents/tools)

---

# 🚀 Quick Demonstration Guide
### Start backend:
```bash
python main.py
```

### Run CLI:
```bash
python demo_cli.py
```

### View Memory:
```
http://127.0.0.1:8000/api/memory/u1
```

---

# 🤖 Gemini Explanation Examples
**Binary Search**  
• *Base:* "Binary search splits a sorted list in half…"  
• *Gemini:* "Binary search efficiently narrows down a sorted list by repeatedly halving it, focusing only on the region where the target can exist."

**Stacks**  
• *Base:* "A stack allows insertion and removal from only one end."  
• *Gemini:* "A stack follows the Last-In, First-Out rule—similar to stacking plates, where the newest plate is always removed first."

---

# ❓ FAQ / Troubleshooting
### **Gemini explanations not appearing?**
- Ensure `.env` exists in project root.
- Ensure it contains:
```
GEMINI_API_KEY=your_key_here
```
- Restart terminal after setting the key.
- Remember: Gemini is optional; fallback explanations still work.

### **Logs folder empty?**
Logs appear **after your first API request**.
Visit:
```
http://127.0.0.1:8000/api/topics
```

### **Evaluator errors?**
Ensure dataset exists: `sample_content_expanded.json`.
Run:
```
p python evaluator.py sample_content_expanded.json
```

### **Memory not updating?**
Delete corrupted `memory.db` and rerun.

### **API connection issues?**
Start server first:
```
python main.py
```
Then retry.

---
### Start backend:
```bash
python main.py

