# main.py (Flask version for Python 3.13)
from flask import Flask, request, jsonify
from agents import Orchestrator
from memory import load_memory, get_history
import json
import asyncio


# -----------------------------
# Load Topic DB
# -----------------------------
with open("sample_content.json", "r") as f:
    TOPIC_DB = json.load(f)


# -----------------------------
# Create Orchestrator
# -----------------------------
orch = Orchestrator(TOPIC_DB, use_llm=False)


# -----------------------------
# Create Flask App
# -----------------------------
app = Flask(__name__)


# -----------------------------
# Helper to run async from Flask
# -----------------------------
def run_async(coro):
    return asyncio.run(coro)


# -----------------------------
# Routes
# -----------------------------

@app.route("/api/learn", methods=["POST"])
def learn():
    data = request.get_json()
    user_id = data.get("user_id")
    topic = data.get("topic").lower()
    mode = data.get("mode")

    try:
        result = run_async(orch.handle(user_id, topic, mode))
        return jsonify({
            "user_id": user_id,
            "topic": topic,
            "mode": mode,
            "result": result
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/grade", methods=["POST"])
def grade():
    data = request.get_json()
    try:
        result = run_async(orch.feedback.grade(
            data["user_id"],
            data["topic"].lower(),
            data["question_id"],
            data["student_answer"],
            data["correct_answer"]
        ))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/memory/<user_id>", methods=["GET"])
def memory_view(user_id):
    try:
        perf = load_memory(user_id, "perf_binary search")
        history = get_history(user_id)
        return jsonify({
            "performance": perf,
            "history": history
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# Run the server
# -----------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
