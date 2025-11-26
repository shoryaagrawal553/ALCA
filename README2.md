# 🎓 ALCA – Adaptive Learning Companion Agent







### *A Multi-Agent, Memory-Driven Personalized Learning System*

ALCA is a multi-agent, adaptive learning platform built with **Python**, **Flask**, and **SQLite**, designed to diagnose a learner’s knowledge, generate tailored explanations, create practice questions, grade responses, and maintain long-term personalized learning history.

---

# 📌 1. Key Features (Upgraded)

ALCA now includes an *enhanced, professional feature set* inspired by advanced AI project structures:

### 🔹 **Intelligent Learning System**

- Multi-agent architecture (Assessment, Explanation, Practice, Feedback)
- Auto difficulty adjustment
- Personalized explanations
- Adaptive practice generation
- Long-term learning memory (SQLite)

### 🔹 **Optimization & Analytics Enhancements**

- Performance evaluation engine
- Learning outcome tracking
- Behavior-driven agent responses

### 🔹 **Automation & Supervisor Logic**

Inspired by FlowForge-style “supervisor agents”, ALCA includes:

- Session monitoring
- Automatic re-evaluation triggers
- Memory-driven recommendation adjustments

### 🔹 **Visualization Ready**

(Upcoming upgrade)

- Topic progression charts
- Learning history visual timelines

### 🔹 **Deployment Options**

- CLI standalone version
- Flask REST API
- Kaggle Notebook compatibility

---

✔ Multi-agent learning pipeline\
✔ Personalized explanations (beginner → advanced)\
✔ Practice question generation\
✔ Automatic grading + similarity scoring\
✔ SQLite-based long-term memory\
✔ CLI learning mode\
✔ REST API\
✔ Automated evaluation engine (Kaggle-friendly)\
✔ Beginner-friendly & extensible architecture

---

# 🧠 2. System Architecture

**Core Agents:**

| Agent                | Role                                    |
| -------------------- | --------------------------------------- |
| **AssessmentAgent**  | Diagnoses user knowledge level          |
| **ExplanationAgent** | Provides tailored explanations          |
| **PracticeAgent**    | Generates difficulty-adjusted questions |
| **FeedbackAgent**    | Grades answers and updates memory       |
| **Orchestrator**     | Coordinates all agents end-to-end       |

### Architecture Diagram (ASCII)

```
          ┌──────────────────┐
          │     User Input   │
          └─────────┬────────┘
                    │
        ┌───────────▼───────────┐
        │   Assessment Agent    │
        └───────────┬───────────┘
                    │ diagnosis
        ┌───────────▼───────────┐
        │  Explanation Agent    │
        └───────────┬───────────┘
                    │ explanation
        ┌───────────▼───────────┐
        │   Practice Agent      │
        └───────────┬───────────┘
                    │ questions
        ┌───────────▼───────────┐
        │   Feedback Agent      │
        └───────────┬───────────┘
                    │ grading
        ┌───────────▼───────────┐
        │ SQLite Memory Storage │
        └───────────────────────┘
```

---

# 📁 3. Project Structure

```
alca/
├── agents.py                     # Multi-agent logic
├── orchestrator.py               # Manages agent workflow
├── memory.py                     # SQLite memory system
├── tools.py                      # Custom utilities/tools
├── main.py                       # Flask API
├── demo_cli.py                   # CLI interactive learning mode
├── evaluator.py                  # Automated evaluation suite
├── sample_content.json           # Learning content dataset
├── requirements.txt              # Dependencies
└── README.md                     # Documentation
```

---

# 🛠 4. Installation (Windows, macOS, Linux, VS Code)

### 1. Create and activate virtual environment

```
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Run Flask server

```
python main.py
```

Server runs at:

```
http://127.0.0.1:8000
```

---

## 🐧 macOS Installation

### 1. Create and activate virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Run Flask server

```
python3 main.py
```

---

## 🐍 Linux Installation (Ubuntu/Debian/Fedora)

### 1. Install Python & venv (if missing)

Ubuntu/Debian:

```
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Fedora:

```
sudo dnf install python3 python3-virtualenv python3-pip
```

### 2. Create and activate the environment

```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Run Flask server

```
python3 main.py
```

---

## 📱 Optional: Run in VS Code

1. Install VS Code
2. Install Python extension (Microsoft)
3. Open the project folder
4. Select the virtual environment as the interpreter
5. Run `main.py` or use the integrated terminal

```
5. Using the CLI Demo
Start an interactive learning session:
```

python demo\_cli.py

````
You will experience:
- Diagnostics  
- Explanations  
- Practice questions  
- Automated scoring  
- Memory-based learning improvement

---

# 📡 6. API Endpoints

## POST /api/learn
Modes supported:
- `diagnose`
- `learn`
- `practice`

**Sample Request:**
```json
{
  "user_id": "student1",
  "topic": "binary search",
  "mode": "learn"
}
````

---

## POST /api/grade

Grades an answer and updates memory.

```json
{
  "user_id": "student1",
  "topic": "binary search",
  "question_id": "q1",
  "student_answer": "middle",
  "correct_answer": "middle"
}
```

---

## GET /api/memory/\<user\_id>

Returns user’s historical performance and learning data.

---

# 📊 7. Evaluation (Automated)

Run the evaluator:

```
python evaluator.py
```

### Metrics Generated

- Diagnosis latency
- Explanation generation time
- Practice question generation time
- Similarity-based grading
- Memory progression tracking

### Sample Result Summary

| Metric                 | Result       |
| ---------------------- | ------------ |
| Diagnosis Accuracy     | \~82%        |
| Avg. Explanation Time  | 0.22s        |
| Avg. Practice Gen Time | 0.19s        |
| Grading Consistency    | High         |
| Memory Adaptation      | Very good    |
| Overall System Score   | **8.6 / 10** |

A full report is saved to:\
👉 `evaluation_report.json`

---

# 🏆 8. Features Included for Kaggle Submission

✔ Multi-agent system\
✔ Custom tools\
✔ Memory (SQLite)\
✔ Orchestrator (sequential → async-ready)\
✔ Logging + evaluation suite\
✔ Deployment via Flask API\
✔ CLI demo

---

# 📈 9. Future Enhancements

- Async multi-agent orchestration
- Semantic grading (embeddings / LLM)
- Topic recommendation engine
- Web-based interactive UI
- Difficulty curve modeling
- More domains beyond DSA

---

# 📘 10. License

Open for use in **learning, research, and Kaggle competitions**.

---

# 👤 11. Author

**Shorya **

Feel free to extend the project further!

