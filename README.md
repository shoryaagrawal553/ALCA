# ALCA: Adaptive Learning Companion Agent

A multi-agent adaptive learning system built using Python, Flask, and SQLite. It provides personalized learning experiences using diagnosis, explanation, practice generation, feedback, and long‑term memory.

---
## 🚀 Overview
ALCA enhances learning by adapting to the student's knowledge level. It uses:
- Multi-agent collaboration
- Memory-based personalization
- Practice question generation
- Real-time grading and feedback
- A simple CLI demo and a Flask API

---
## 🧠 System Architecture
**Agents Included:**
- **AssessmentAgent** – Diagnoses user’s knowledge using diagnostic questions
- **ExplanationAgent** – Provides level-adapted explanation
- **PracticeAgent** – Generates practice questions based on difficulty
- **FeedbackAgent** – Grades answers and updates memory
- **Orchestrator** – Coordinates multiple agents asynchronously

**Tools:**
- Code evaluation utility
- Simple search

**Storage:**
- SQLite-based memory for user progress & session history

---
## 📁 Project Structure
```
alca/
├── agents.py
├── memory.py
├── tools.py
├── main.py
├── demo_cli.py
├── evaluator.py
├── sample_content.json
├── requirements.txt
└── README.md
```

---
## ▶️ Running the Project
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
## 🧪 Using the CLI Demo
Interactive terminal-based learning session:
```
python demo_cli.py
```
You will:
- Receive diagnostic questions
- Get explanations
- Solve practice questions
- Receive grading & memory overview

---
## 📡 API Endpoints
### **POST /api/learn**
Modes:
- `diagnose`
- `learn`
- `practice`

**Request Body:**
```json
{
  "user_id": "student1",
  "topic": "binary search",
  "mode": "learn"
}
```

### **POST /api/grade**
Grades an answer and updates memory.

**Request Body:**
```json
{
  "user_id": "student1",
  "topic": "binary search",
  "question_id": "q1",
  "student_answer": "middle",
  "correct_answer": "middle"
}
```

### **GET /api/memory/<user_id>**
Returns user performance and session history.

---
## 📊 Evaluation
Run automated evaluation:
```
python evaluator.py
```
Metrics reported:
- Diagnosis time
- Explanation generation time
- Practice generation time
- Questions generated
- Grading checks
- Memory state after evaluation

---
## 🏆 Features for Kaggle Submission
- Multi-agent system
- Persistent memory
- Async orchestration
- Tool usage
- Automated evaluation
- API + CLI demonstration

---
## 📘 License
Open for use in learning, research, and Kaggle competitions.

---
## 👤 Author
Shorya — CSE Student

Feel free to extend this project by adding:
- More topics
- Difficulty scaling
- User interface
- OpenAI/Anthropic LLM integration

