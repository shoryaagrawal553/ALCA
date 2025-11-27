import json
import os
import logging
from logging.handlers import RotatingFileHandler
import functools
import time
from flask import Flask, request, jsonify
from agents import Orchestrator
from memory import MemoryManager
from evaluator import Evaluator, evaluate_answer  
# -------------------------
# Paths
# -------------------------
LOG_DIR = "logs"
SESSION_DIR = "sessions"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)

# -------------------------
# Logging Setup
# -------------------------
def make_rotating_handler(path, level=logging.INFO, maxBytes=5*1024*1024, backupCount=3):
    handler = RotatingFileHandler(path, maxBytes=maxBytes, backupCount=backupCount)
    handler.setLevel(level)
    fmt = logging.Formatter("[%(asctime)s] %(levelname)s — %(name)s — %(message)s")
    handler.setFormatter(fmt)
    return handler

# Root logger (app)
logger_app = logging.getLogger("alca.app")
logger_app.setLevel(logging.INFO)
logger_app.addHandler(make_rotating_handler(os.path.join(LOG_DIR, "app.log")))

# API loggers (separate files per endpoint as requested A1)
logger_api_learn = logging.getLogger("alca.api.learn")
logger_api_learn.setLevel(logging.INFO)
logger_api_learn.addHandler(make_rotating_handler(os.path.join(LOG_DIR, "api_learn.log")))

logger_api_memory = logging.getLogger("alca.api.memory")
logger_api_memory.setLevel(logging.INFO)
logger_api_memory.addHandler(make_rotating_handler(os.path.join(LOG_DIR, "api_memory.log")))

logger_api_evaluate = logging.getLogger("alca.api.evaluate")
logger_api_evaluate.setLevel(logging.INFO)
logger_api_evaluate.addHandler(make_rotating_handler(os.path.join(LOG_DIR, "api_evaluate.log")))

# Agents logger
logger_agents = logging.getLogger("alca.agents")
logger_agents.setLevel(logging.INFO)
logger_agents.addHandler(make_rotating_handler(os.path.join(LOG_DIR, "agents.log")))

# Evaluator logger
logger_evaluator = logging.getLogger("alca.evaluator")
logger_evaluator.setLevel(logging.INFO)
logger_evaluator.addHandler(make_rotating_handler(os.path.join(LOG_DIR, "evaluator.log")))

# Console handler (optional, helpful during development)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s — %(name)s — %(message)s"))
logger_app.addHandler(console)
logger_agents.addHandler(console)

# -------------------------
# Helpers: timing decorator
# -------------------------
def log_timing(api_logger):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            start = time.time()
            try:
                api_logger.info(f"ENTER {fn.__name__} - path={request.path} payload={request.get_json(silent=True)}")
            except Exception:
                api_logger.info(f"ENTER {fn.__name__}")
            result = None
            try:
                result = fn(*args, **kwargs)
                return result
            finally:
                elapsed = (time.time() - start) * 1000.0
                api_logger.info(f"EXIT  {fn.__name__} - took={elapsed:.1f}ms")
        return wrapped
    return decorator

# -------------------------
# session manager 
# -------------------------
def store_session(user_id: str, session_data: dict):
    path = os.path.join(SESSION_DIR, f"{user_id}.jsonl")
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.time(), "data": session_data}) + "\n")
        logger_app.info(f"Stored session for user={user_id}")
    except Exception as e:
        logger_app.exception(f"Failed to store session for {user_id}: {e}")
        raise

def get_last_session(user_id: str):
    path = os.path.join(SESSION_DIR, f"{user_id}.jsonl")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().strip().splitlines()
            if not lines:
                return None
            last = json.loads(lines[-1])
            return last
    except Exception as e:
        logger_app.exception(f"Failed to read session for {user_id}: {e}")
        return None

# -------------------------
# Core LearningSystem 
# -------------------------
class LearningSystem:
    def __init__(self, content_file="sample_content_expanded.json", user_id="default"):
        self.user_id = user_id
        self.memory = MemoryManager()
        self.content = self.load_content(content_file)
        self.agent = Orchestrator(self.content, self.memory)

    def load_content(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def choose_difficulty(self, topic):
        stats = self.memory.get_user_topic_stats(self.user_id, topic)
        accuracy = stats["accuracy"]

        if accuracy < 40:
            return "beginner"
        elif accuracy < 75:
            return "intermediate"
        else:
            return "advanced"

    def get_question(self, topic):
        difficulty = self.choose_difficulty(topic)
        questions = self.content[topic]["practice"]

        filtered = [q for q in questions if q["difficulty"] == difficulty]
        if not filtered:
            filtered = questions

        return filtered[0]

    def run_step(self, topic, student_answer):
        q = self.get_question(topic)
        correct = evaluate_answer(student_answer, q["answer"])

        self.memory.record_attempt(
            user_id=self.user_id,
            topic=topic,
            question_id=q["id"],
            student_answer=student_answer,
            correct_answer=q["answer"],
            is_correct=correct
        )

        explanation_level = self.choose_difficulty(topic)
        explanation = self.content[topic]["explanations"][explanation_level]

        return {
            "question": q["question"],
            "correct": correct,
            "correct_answer": q["answer"],
            "your_answer": student_answer,
            "explanation_level": explanation_level,
            "explanation": explanation,
            "stats": self.memory.get_user_topic_stats(self.user_id, topic)
        }

    def get_summary(self):
        return self.memory.get_user_summary(self.user_id)

# -------------------------
# Flask API
# -------------------------
app = Flask(__name__)

@app.post("/api/learn")
@log_timing(logger_api_learn)
def api_learn():
    data = request.get_json() or {}
    user_id = data.get("user_id", "default")
    topic = data.get("topic")
    answer = data.get("answer", "")

    logger_api_learn.info(f"Request /api/learn user_id={user_id} topic={topic} answer_provided={'yes' if answer else 'no'}")

    ls = LearningSystem(user_id=user_id)

    if not topic:
        logger_api_learn.warning(f"/api/learn called without topic by {user_id}")
        return jsonify({"error": "topic is required"}), 400

    # if no answer supplied -> return a question
    if answer == "":
        q = ls.get_question(topic)
        # store session preview
        store_session(user_id, {"action": "serve_question", "topic": topic, "question_id": q["id"]})
        logger_api_learn.info(f"Served question id={q['id']} for user={user_id} topic={topic}")
        return jsonify({
            "question": q["question"],
            "question_id": q["id"]
        })

    # answer path
    result = ls.run_step(topic, answer)
    # store session after attempt
    store_session(user_id, {"action": "answer", "topic": topic, "question_id": result.get("question_id", None)})
    logger_api_learn.info(f"User {user_id} answered question on topic={topic} correct={result['correct']}")
    return jsonify(result)


@app.get("/api/memory/<user_id>")
@log_timing(logger_api_memory)
def api_memory(user_id):
    logger_api_memory.info(f"/api/memory requested for user_id={user_id}")
    ls = LearningSystem(user_id=user_id)
    summary = ls.get_summary()
    return jsonify(summary)


@app.get("/api/topics")
@log_timing(logger_api_learn)  # reuse learn logger as topic listing is tied to learning
def api_topics():
    # Provide a brief list of available topics and counts
    try:
        with open("sample_content_expanded.json", "r", encoding="utf-8") as f:
            content = json.load(f)
    except Exception as e:
        logger_app.exception("Failed to load content file for /api/topics")
        return jsonify({"error": "Failed to load content"}), 500

    topics = {k: {"has_practice": ("practice" in v), "has_explanations": ("explanations" in v)} for k, v in content.items()}
    logger_api_learn.info(f"Serving /api/topics list ({len(topics)} topics)")
    return jsonify({"topics": topics})


@app.post("/api/session/store")
@log_timing(logger_api_learn)
def api_store_session():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    payload = data.get("payload", {})
    if not user_id:
        logger_api_learn.warning("/api/session/store called without user_id")
        return jsonify({"error": "user_id required"}), 400
    try:
        store_session(user_id, payload)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.get("/api/session/<user_id>")
@log_timing(logger_api_memory)
def api_get_session(user_id):
    last = get_last_session(user_id)
    if not last:
        return jsonify({"status": "empty"})
    return jsonify(last)


# ------------------------------------------------
# /api/evaluate 
# ------------------------------------------------
@app.post("/api/evaluate")
@log_timing(logger_api_evaluate)
def api_evaluate():
    try:
        logger_api_evaluate.info("Starting full evaluation run")
        evaluator = Evaluator()  # your evaluator class
        report = evaluator.run_full_evaluation()
        logger_evaluator.info("Evaluator finished run_full_evaluation")
        return jsonify({
            "status": "success",
            "results": report
        })
    except Exception as e:
        logger_api_evaluate.exception("Evaluation failed")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# -------------------------
# Run Server
# -------------------------
if __name__ == "__main__":
    logger_app.info("Starting ALCA Flask server at 127.0.0.1:8000")
    app.run(host="127.0.0.1", port=8000, debug=False)
