import random
import logging
from memory import MemoryManager

# Acquire agents logger (configured in main.py)
logger_agents = logging.getLogger("alca.agents")

class AssessmentAgent:
    """Asks diagnostic questions for a topic."""

    def __init__(self, db):
        self.db = db

    def ask(self, topic):
        topic_data = self.db.get(topic)
        if not topic_data:
            logger_agents.warning(f"AssessmentAgent.ask: unknown topic={topic}")
            return None

        q = random.choice(topic_data["diagnostic"])
        logger_agents.info(f"AssessmentAgent.ask topic={topic} qid={q.get('id') if isinstance(q, dict) else 'n/a'}")
        return q


class ExplanationAgent:
    """Gives explanation for a topic based on difficulty level."""

    def __init__(self, db):
        self.db = db

    def explain(self, topic, level="beginner"):
        topic_data = self.db.get(topic)
        if not topic_data:
            logger_agents.warning(f"ExplanationAgent.explain: unknown topic={topic}")
            return None

        levels = topic_data["explanations"]
        res = levels.get(level, levels.get("beginner"))
        logger_agents.info(f"ExplanationAgent.explain topic={topic} level={level}")
        return res


class PracticeAgent:
    """Generates random practice questions."""

    def __init__(self, db):
        self.db = db

    def generate(self, topic, difficulty=None):
        topic_data = self.db.get(topic)
        if not topic_data:
            logger_agents.warning(f"PracticeAgent.generate: unknown topic={topic}")
            return None

        questions = topic_data["practice"]

        if difficulty:
            filtered = [q for q in questions if q["difficulty"] == difficulty]
            if filtered:
                q = random.choice(filtered)
                logger_agents.info(f"PracticeAgent.generate topic={topic} difficulty={difficulty} qid={q.get('id')}")
                return q

        q = random.choice(questions)
        logger_agents.info(f"PracticeAgent.generate topic={topic} fallback qid={q.get('id')}")
        return q


class FeedbackAgent:
    """Grades answer and updates memory."""

    def __init__(self, memory: MemoryManager):
        self.memory = memory

    def grade(self, user_id, topic, qid, student_answer, correct_answer):
        correct = (student_answer.strip().lower() == correct_answer.strip().lower())
        self.memory.record_attempt(user_id, topic, qid, student_answer, correct_answer, correct)
        logger_agents.info(f"FeedbackAgent.grade user={user_id} topic={topic} qid={qid} correct={correct}")
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
        logger_agents.info(f"Orchestrator.handle user={user_id} topic={topic} mode={mode}")
        if topic not in self.db:
            logger_agents.warning(f"Orchestrator.handle unknown topic={topic}")
            return {"error": "Unknown topic"}

        if mode == "diagnose":
            q = self.assessment_agent.ask(topic)
            return {"type": "diagnostic", "question": q}

        elif mode == "learn":
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
            logger_agents.warning(f"Orchestrator.handle unknown mode={mode}")
            return {"error": "Unknown mode"}

    def grade_answer(self, user_id, topic, qid, ans, correct):
        logger_agents.info(f"Orchestrator.grade_answer user={user_id} topic={topic} qid={qid} ans={ans} correct={correct}")
        return self.feedback_agent.grade(user_id, topic, qid, ans, correct)
