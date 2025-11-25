import json
from agents import TutorAgent
from memory import MemoryManager
from evaluator import evaluate_answer


class LearningSystem:
    def __init__(self, content_file="sample_content_expanded.json", user_id="default"):
        self.user_id = user_id
        self.memory = MemoryManager()
        self.content = self.load_content(content_file)
        self.agent = TutorAgent(self.content)

    # ------------------------------------------------
    # Load dataset
    # ------------------------------------------------
    def load_content(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ------------------------------------------------
    # Choose difficulty level based on statistics
    # ------------------------------------------------
    def choose_difficulty(self, topic):
        stats = self.memory.get_user_topic_stats(self.user_id, topic)
        accuracy = stats["accuracy"]

        if accuracy < 40:
            return "beginner"
        elif accuracy < 75:
            return "intermediate"
        else:
            return "advanced"

    # ------------------------------------------------
    # Pick a practice question
    # ------------------------------------------------
    def get_question(self, topic):
        difficulty = self.choose_difficulty(topic)
        questions = self.content[topic]["practice"]

        filtered = [q for q in questions if q["difficulty"] == difficulty]

        if not filtered:  # fallback
            filtered = questions

        return filtered[0]  # simple deterministic selection

    # ------------------------------------------------
    # Run a single tutoring step
    # ------------------------------------------------
    def run_step(self, topic, student_answer):
        # Fetch question
        q = self.get_question(topic)

        # Evaluate correctness
        correct = evaluate_answer(student_answer, q["answer"])

        # Memory update
        self.memory.record_attempt(
            user_id=self.user_id,
            topic=topic,
            question_id=q["id"],
            student_answer=student_answer,
            correct_answer=q["answer"],
            is_correct=correct
        )

        # Tutor feedback
        explanation_level = self.choose_difficulty(topic)
        explanation = self.content[topic]["explanations"][explanation_level]

        result = {
            "question": q["question"],
            "correct": correct,
            "correct_answer": q["answer"],
            "your_answer": student_answer,
            "explanation_level": explanation_level,
            "explanation": explanation,
            "stats": self.memory.get_user_topic_stats(self.user_id, topic)
        }

        return result

    # ------------------------------------------------
    # Full user summary (for dashboard or CLI command)
    # ------------------------------------------------
    def get_summary(self):
        return self.memory.get_user_summary(self.user_id)


# ------------------------------------------------------
# Demo CLI Driver
# ------------------------------------------------------
if __name__ == "__main__":
    ls = LearningSystem()

    print("=== Adaptive Learning CLI ===")
    topic = input("Enter topic: ").strip().lower()

    q = ls.get_question(topic)
    print("\nQuestion:", q["question"])

    ans = input("Your Answer: ")

    result = ls.run_step(topic, ans)
    print("\n--- Result ---")
    print("Correct?", result["correct"])
    print("Correct Answer:", result["correct_answer"])
    print("Explanation (", result["explanation_level"], "):")
    print(result["explanation"])
    print("Stats:", result["stats"])
