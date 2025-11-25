import random
from memory import MemoryManager


class AssessmentAgent:
    """Asks diagnostic questions for a topic."""

    def __init__(self, db):
        self.db = db

    def ask(self, topic):
        topic_data = self.db.get(topic)
        if not topic_data:
            return None

        # pick a random diagnostic question
        return random.choice(topic_data["diagnostic"])     


class ExplanationAgent:
    """Gives explanation for a topic based on difficulty level."""

    def __init__(self, db):
        self.db = db

    def explain(self, topic, level="beginner"):
        topic_data = self.db.get(topic)
        if not topic_data:
            return None

        levels = topic_data["explanations"]

        # gracefully fallback to beginner
        return levels.get(level, levels["beginner"])


class PracticeAgent:
    """Generates random practice questions."""

    def __init__(self, db):
        self.db = db

    def generate(self, topic, difficulty=None):
        topic_data = self.db.get(topic)
        if not topic_data:
            return None

        questions = topic_data["practice"]

        if difficulty:
            filtered = [q for q in questions if q["difficulty"] == difficulty]
            if filtered:
                return random.choice(filtered)

        # fallback: return any random practice question
        return random.choice(questions)


class FeedbackAgent:
    """Grades answer and updates memory."""

    def __init__(self, memory: MemoryManager):
        self.memory = memory

    def grade(self, user_id, topic, qid, student_answer, correct_answer):
        correct = (student_answer.strip().lower() == correct_answer.strip().lower())

        self.memory.record_attempt(user_id, topic, qid, correct)

        return {
            "correct": correct,
            "correct_answer": correct_answer,
            "student_answer": student_answer,
        }


class Orchestrator:
    """Coordinates all agents."""

    def __init__(self, db, memory: MemoryManager):
        self.db = db
        self.memory = memory

        self.assessment_agent = AssessmentAgent(db)
        self.explanation_agent = ExplanationAgent(db)
        self.practice_agent = PracticeAgent(db)
        self.feedback_agent = FeedbackAgent(memory)

    def handle(self, user_id, topic, mode):
        if topic not in self.db:
            return {"error": "Unknown topic"}

        if mode == "diagnose":
            q = self.assessment_agent.ask(topic)
            return {"type": "diagnostic", "question": q}

        elif mode == "learn":
            # choose explanation difficulty based on past performance
            past = self.memory.get_user_topic_stats(user_id, topic)

            if past is None:
                level = "beginner"
            else:
                accuracy = past["accuracy"]
                if accuracy < 0.4:
                    level = "beginner"
                elif accuracy < 0.7:
                    level = "intermediate"
                else:
                    level = "advanced"

            ex = self.explanation_agent.explain(topic, level)
            return {"type": "explanation", "level": level, "explanation": ex}

        elif mode == "practice":
            # adapt difficulty using memory
            past = self.memory.get_user_topic_stats(user_id, topic)

            if past is None:
                diff = "beginner"
            else:
                accuracy = past["accuracy"]
                if accuracy < 0.4:
                    diff = "beginner"
                elif accuracy < 0.7:
                    diff = "intermediate"
                else:
                    diff = "advanced"

            q = self.practice_agent.generate(topic, diff)
            return {"type": "practice", "difficulty": diff, "question": q}

        else:
            return {"error": "Unknown mode"}

    def grade_answer(self, user_id, topic, qid, ans, correct):
        return self.feedback_agent.grade(user_id, topic, qid, ans, correct)
