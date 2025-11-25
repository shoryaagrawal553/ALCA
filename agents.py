# agents.py
import asyncio
import json
import random
import time
from typing import Any, Dict, Optional

from memory import (
    save_memory,
    load_memory,
    append_session
)

from tools import (
    evaluate_python_code,
    simple_search
)

import logging
logger = logging.getLogger("alca")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
logger.addHandler(handler)


# ------------------------------------------------------------
#  SIMPLE MOCK LLM (used for explanations when no API is used)
# ------------------------------------------------------------
def mock_llm(prompt: str, temperature: float = 0.0) -> str:
    """
    A deterministic mock 'LLM' to provide placeholder text
    without needing a real API key.
    """
    p = prompt.lower()

    if "explain" in p:
        if "beginner" in p:
            return "Beginner explanation: Let's break this topic into simple parts..."
        if "intermediate" in p:
            return "Intermediate explanation: Here's a more detailed explanation..."
        return "Advanced explanation: Let's go deeper into technical concepts..."

    if "generate question" in p:
        return json.dumps({
            "question": "What is the time complexity of binary search?",
            "difficulty": "beginner",
            "answer": "O(log n)"
        })

    return "I am a mock LLM responding to your prompt."


# ------------------------------------------------------------
# 1. ASSESSMENT AGENT
# ------------------------------------------------------------
class AssessmentAgent:
    """Diagnoses the user's initial understanding of a topic."""

    def __init__(self, topic_db: Dict[str, Any]):
        self.topic_db = topic_db

    async def diagnose(self, user_id: str, topic: str) -> Dict[str, Any]:
        logger.info(f"AssessmentAgent diagnosing user {user_id} on {topic}")

        data = self.topic_db.get(topic)
        if not data:
            # fallback: first topic
            data = list(self.topic_db.values())[0]

        questions = data.get("diagnostic", [])

        # Check if user already has a memory entry for this topic
        existing = load_memory(user_id, f"known_{topic}")
        estimated_level = existing["level"] if existing else "unknown"

        result = {
            "diagnostic": questions,
            "estimated_level": estimated_level
        }

        append_session(user_id, topic, "diagnose", result)
        return result


# ------------------------------------------------------------
# 2. EXPLANATION AGENT
# ------------------------------------------------------------
class ExplanationAgent:
    """Explains the topic at the user's level."""

    def __init__(self, topic_db: Dict[str, Any], use_llm: bool = False):
        self.topic_db = topic_db
        self.use_llm = use_llm

    async def explain(self, user_id: str, topic: str, level: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"ExplanationAgent explaining {topic} to {user_id} at level {level}")

        data = self.topic_db.get(topic)
        if not data:
            data = list(self.topic_db.values())[0]

        level = level or "intermediate"

        if self.use_llm:
            prompt = f"Explain {topic} for a {level} student: {data.get('concept', '')}"
            explanation = mock_llm(prompt)
        else:
            explanation = data["explanations"].get(level, data["explanations"]["intermediate"])

        result = {
            "explanation": explanation,
            "level": level
        }

        append_session(user_id, topic, "explain", result)
        return result


# ------------------------------------------------------------
# 3. PRACTICE AGENT
# ------------------------------------------------------------
class PracticeAgent:
    """Generates adaptive practice questions."""

    def __init__(self, topic_db: Dict[str, Any]):
        self.topic_db = topic_db

    async def generate_practice(self, user_id: str, topic: str, level: str = "intermediate", n: int = 3) -> Dict[str, Any]:
        logger.info(f"PracticeAgent generating practice for {user_id} on {topic} at {level}")

        data = self.topic_db.get(topic)
        if not data:
            data = list(self.topic_db.values())[0]

        # Pick questions matching the level
        selected = []
        for q in data.get("practice", []):
            if q["difficulty"] == level:
                selected.append(q)
            if len(selected) >= n:
                break

        # If not enough questions, sample
        if not selected:
            selected = random.sample(data.get("practice", []), min(n, len(data["practice"])))

        result = {"practice": selected}
        append_session(user_id, topic, "practice", result)
        return result


# ------------------------------------------------------------
# 4. FEEDBACK AGENT
# ------------------------------------------------------------
class FeedbackAgent:
    """Grades student answers and updates memory."""

    async def grade(
        self,
        user_id: str,
        topic: str,
        question_id: str,
        user_answer: str,
        correct_answer: str
    ) -> Dict[str, Any]:

        logger.info(f"FeedbackAgent grading user {user_id} for {question_id}")

        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

        result = {
            "question_id": question_id,
            "user_answer": user_answer,
            "correct": is_correct,
            "expected": correct_answer
        }

        append_session(user_id, topic, "grade", result)

        # Update user performance memory
        performance = load_memory(user_id, f"perf_{topic}") or {"correct": 0, "total": 0}
        performance["total"] += 1
        if is_correct:
            performance["correct"] += 1

        save_memory(user_id, f"perf_{topic}", performance)

        # If accuracy is high → mark topic as "known"
        if performance["total"] >= 3:
            accuracy = performance["correct"] / performance["total"]
            if accuracy >= 0.75:
                save_memory(user_id, f"known_{topic}", {"level": "intermediate", "timestamp": int(time.time())})

        return result


# ------------------------------------------------------------
# 5. ORCHESTRATOR (THE BRAIN)
# ------------------------------------------------------------
class Orchestrator:
    """Coordinates multiple agents and builds a full learning session."""

    def __init__(self, topic_db: Dict[str, Any], use_llm: bool = False):
        self.assessment = AssessmentAgent(topic_db)
        self.explainer = ExplanationAgent(topic_db, use_llm)
        self.practice = PracticeAgent(topic_db)
        self.feedback = FeedbackAgent()

    async def handle(self, user_id: str, topic: str, mode: str) -> Dict[str, Any]:
        """
        mode options:
        - diagnose
        - learn
        - practice
        """

        if mode == "diagnose":
            return await self.assessment.diagnose(user_id, topic)

        if mode == "learn":
            # 1 → Diagnose
            diag = await self.assessment.diagnose(user_id, topic)
            level = diag["estimated_level"] if diag["estimated_level"] != "unknown" else "beginner"

            # 2 → Parallel: explanation + practice
            explanation_task = asyncio.create_task(
                self.explainer.explain(user_id, topic, level)
            )

            practice_task = asyncio.create_task(
                self.practice.generate_practice(user_id, topic, level)
            )

            explanation, practice = await asyncio.gather(explanation_task, practice_task)

            return {
                "diagnostic": diag,
                "explanation": explanation,
                "practice": practice
            }

        if mode == "practice":
            perf = load_memory(user_id, f"perf_{topic}") or {}
            level = "beginner"

            if perf:
                accuracy = perf["correct"] / max(1, perf["total"])
                if accuracy >= 0.8:
                    level = "advanced"
                elif accuracy > 0.5:
                    level = "intermediate"

            return await self.practice.generate_practice(user_id, topic, level)

        return {"error": "unknown mode"}
