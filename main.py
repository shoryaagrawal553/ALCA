import json
from flask import Flask, request, jsonify
from agents import TutorAgent
from memory import MemoryManager
from evaluator import evaluate_answer, Evaluator

app = Flask(__name__)


# ------------------------------------------------
# Core Learning System
# ------------------------------------------------
class LearningSystem:
    def __init__(self, content_file="sample_content_expanded.json", user_id="default"):
        self.user_id = user_id
        self.memory = MemoryManager()
        self.content = self.load_content(content_file)
        self.agent = TutorAgent(self.content)

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


# ------------------------------------------------
# Flask API
# ------------------------------------------------

@app.post("/api/learn")
def api_learn():
    data = request.get_json()
    user_id = data.get("user_id", "default")
    topic = data.get("topic")
    answer = data.get("answer", "")

    ls = LearningSystem(user_id=user_id)

    if answer == "":
        q = ls.get_question(topic)
        return jsonify({
            "question": q["question"],
            "question_id": q["id"]
        })

    result = ls.run_step(topic, answer)
    return jsonify(result)


@app.get("/api/memory/<user_id>")
def api_memory(user_id):
    ls = LearningSystem(user_id=user_id)
    return jsonify(ls.get_summary())


# ------------------------------------------------
# NEW: /api/evaluate
# ------------------------------------------------
@app.post("/api/evaluate")
def api_evaluate():
    try:
        evaluator = Evaluator()
        report = evaluator.run_full_evaluation()

        return jsonify({
            "status": "success",
            "results": report
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ------------------------------------------------
# Run Server
# ------------------------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
