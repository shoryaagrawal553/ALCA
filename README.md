# 📘 ALCA — Adaptive Learning Companion Agent

## 📑 Table of Contents

1. [Features Overview](#-features-overview)
2. [System Architecture](#-system-architecture)
3. [Project Structure](#-project-structure)
4. [Getting Started](#-getting-started)
5. [Using ALCA](#-using-alca)
   - [Get Topics](#-1-get-topics)
   - [Request a Question](#-2-request-a-question)
   - [Submit an Answer](#-3-submit-an-answer)
   - [Get Memory](#-4-get-memory)
   - [Session Management](#-5-session-management)
   - [Run Evaluator](#-6-run-evaluator-judging-tool)
6. [CLI Demo](#-cli-demo-user-mode)
7. [Observability & Logging](#-observability--logging)
8. [How It Works Internally](#-how-it-works-internally-high-level)
9. [2‑Minute Demo Script](#-2-minute-demo-script-for-judges)
10. [Project Badges](#-project-badges-visual-polish)
11. [Why ALCA Is Competition-Ready](#-why-alca-is-competition-ready)
12. [License](#-license)
13. [Final Notes](#-alca-is-ready-for-submission)



*A Multi-Agent, Tool-Based, Memory-Driven Learning System*

ALCA is an adaptive learning platform built using **multi-agent architecture**, **custom tools**, **memory with SQLite**, **observability/logging**, **evaluation pipeline**, and a **REST API + CLI interface**.

It dynamically diagnoses learner knowledge, explains concepts at the right difficulty level, gives adaptive practice questions, evaluates answers, and tracks long-term progress.

---

# 🚀 Features Overview

| Capability             | Description                                                                            |
| ---------------------- | -------------------------------------------------------------------------------------- |
| **Multi-Agent System** | Diagnostic, Explanation, Practice, and Feedback agents coordinated by an orchestrator. |
| **Tools**              | Code execution, simple search, dataset-driven evaluation tools.                        |
| **Memory & Sessions**  | SQLite-based memory manager + session storage in JSONL format.                         |
| **Observability**      | Rotating logs for app, API, agents, evaluator; timing logs for every endpoint.         |
| **Evaluator**          | Automated evaluation across all topics (latency, scoring, practice accuracy).          |
| **APIs**               | /api/learn, /api/topics, /api/memory, /api/session, /api/evaluate                      |
| **CLI Demo**           | Fully interactive terminal experience for end-users.                                   |

---

# 🧠 System Architecture

```
                   ┌────────────────────────────────┐
                   │          ALCA System           │
                   └────────────────────────────────┘
                                │
       ┌────────────────────────┼────────────────────────┐
       │                        │                        │
┌──────────────┐        ┌───────────────┐      ┌─────────────────┐
│ Diagnostics  │        │ Explanation   │      │ Practice Agent  │
│   Agent      │        │   Agent       │      │ (Adaptive Qs)   │
└──────────────┘        └───────────────┘      └─────────────────┘
                      (topic + difficulty)
                                │
                         ┌────────────┐
                         │ Feedback   │
                         │   Agent    │
                         └────────────┘
                                │
                         Updates Memory
                                │
                    ┌─────────────────────┐
                    │  MemoryManager.db   │
                    └─────────────────────┘

                      ┌───────────────────┐
                      │   Orchestrator    │
                      └───────────────────┘
                                │
                ┌─────────────────────────────────┐
                │     REST API / CLI Interface    │
                └─────────────────────────────────┘
```

---

# 📂 Project Structure

```
ALCA/
│
├── main.py                     # Flask API + Logging + Sessions
├── agents.py                   # Multi-agent system
├── memory.py                   # SQLite memory manager
├── tools.py                    # Tools: code executor, search
├── evaluator.py                # Auto evaluator
├── demo_cli.py                 # Interactive CLI for users
│
├── sample_content_expanded.json
├── sample_content.json
│
├── logs/                       # Observability logs (auto-generated)
│   ├── app.log
│   ├── agents.log
│   ├── api_learn.log
│   ├── api_memory.log
│   ├── api_evaluate.log
│   └── evaluator.log
│
├── sessions/                   # Persistent user sessions
│
└── requirements.txt
```

---

# 🏃 Getting Started

## 1. Install dependencies

```
pip install -r requirements.txt
```

## 2. Run the server

```
python main.py
```

Server starts at:

```
http://127.0.0.1:8000
```

---

# 🖥 Using ALCA

## ✔ 1. Get Topics

```
GET /api/topics
```

Example output:

```json
{
    "topics": [
        {"name": "stacks", "has_explanations": true, "has_practice": true},
        {"name": "queues", "has_explanations": true, "has_practice": true}
    ]
}
```

---

## ✔ 2. Request a Question

```
POST /api/learn
{
  "user_id": "u1",
  "topic": "stacks",
  "answer": ""
}
```

---

## ✔ 3. Submit an Answer

```
POST /api/learn
{
  "user_id": "u1",
  "topic": "stacks",
  "answer": "LIFO"
}
```

Returns:

- correctness
- explanation
- difficulty level
- updated stats

---

## ✔ 4. Get Memory

```
GET /api/memory/u1
```

---

## ✔ 5. Session Management

### Store session:

```
POST /api/session/store
{"user_id":"u1", "payload":{"last_topic":"stacks"}}
```

### Retrieve session:

```
GET /api/session/u1
```

---

## ✔ 6. Run Evaluator (Judging Tool)

```
python evaluator.py sample_content_expanded.json
```

Produces:

```
evaluation_report.json
```

Includes:

- topic latency
- average correctness
- accuracy trends
- question counts

---

# 🧪 CLI Demo (User Mode)

```
python demo_cli.py
```

Provides:

- topic list
- diagnostic
- explanation
- practice
- grading
- summary

This is the preferred mode for human users.

---

# 📊 Observability & Logging

All logs stored in `logs/`:

- app.log — server start, API loading
- agents.log — every agent call
- api\_learn.log — learning requests
- api\_memory.log — memory requests
- api\_evaluate.log — evaluator requests
- evaluator.log — metrics & scoring

Each request includes:

- timestamp
- agent invoked
- user\_id
- topic
- latency (ms)

---

# 🧩 Requirement-to-Feature Mapping

ALCA directly satisfies **all required capstone concepts**:

✔ Multi-Agent System\
✔ Orchestrator\
✔ Custom Tools\
✔ Sessions & Memory\
✔ Observability (Logging + Timing)\
✔ Evaluation Pipeline\
✔ Dataset Integration\
✔ Clean APIs + CLI Demo\
✔ Fully Modular Architecture

All features are lightweight, clean, and professionally structured.

---

# 📄 License

MIT License

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

Use this script during your evaluation presentation:

### **1️⃣ Start ALCA**

```bash
python main.py
```

Say: *"The ALCA backend is now running with full logging and observability."*

### **2️⃣ Run the CLI Demo**

```bash
python demo_cli.py
```

Say:

- *"ALCA begins by diagnosing your understanding."*
- *"It then provides explanations based on difficulty."*
- *"Finally, it gives adaptive practice and updates memory automatically."*

### **3️⃣ Show Memory Dashboard**

Open:

```
http://127.0.0.1:8000/api/memory/u1
```

Say: *"ALCA tracks accuracy, attempts, and history per topic using SQLite."*

### **4️⃣ Show Logs**

Open the `/logs` folder. Say: *"ALCA logs every agent call, API request, evaluator run, and performance metric."*

### **5️⃣ Run the Evaluator**

```bash
python evaluator.py sample_content_expanded.json
```

Say: *"The evaluator runs multi-topic analysis for latency, scoring, and correctness."*

### **6️⃣ End With Topics API**

```
http://127.0.0.1:8000/api/topics
```

Say: *"All topics and capabilities are cleanly exposed via REST APIs."*

---

# 🏷️ Project Badges (Visual Polish)

Add these badges at the top of the README for a professional look:

```
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Agents](https://img.shields.io/badge/AI-Multi--Agent-orange)
```

---

# 🎉 ALCA is Ready for Submission

You now have a fully functional, clean, production-grade capstone project.

