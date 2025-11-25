from flask import Flask, request, jsonify
import json
from agents import Orchestrator
from memory import MemoryManager

app = Flask(__name__)

# Load expanded dataset
with open("sample_content_expanded.json", "r") as f:
    DB = json.load(f)

# Initialize orchestrator + memory
memory = MemoryManager()
orch = Orchestrator(DB, memory)


@app.route("/")
def home():
    return {"message": "ALCA API Running", "topics": list(DB.keys())}


@app.route("/api/topics", methods=["GET"])
def list_topics():
    return jsonify({"topics": list(DB.keys())})


@app.route("/api/learn", methods=["POST"])
def learn():
    data = request.json

    user_id = data.get("user_id")
    topic = data.get("topic")
    mode = data.get("mode")  # "diagnose", "learn", "practice"

    if topic not in DB:
        return jsonify({"error": "Unknown topic", "available_topics": list(DB.keys())}), 400

    result = orch.handle(user_id, topic, mode)
    return jsonify(result)


@app.route("/api/grade", methods=["POST"])
def grade():
    data = request.json

    user_id = data.get("user_id")
    topic = data.get("topic")
    qid = data.get("question_id")
    ans = data.get("student_answer")
    correct = data.get("correct_answer")

    result = orch.grade_answer(user_id, topic, qid, ans, correct)
    return jsonify(result)


@app.route("/api/memory/<user_id>", methods=["GET"])
def memory_get(user_id):
    return jsonify(memory.get_user(user_id))


if __name__ == "__main__":
    app.run(port=8000, debug=True)
