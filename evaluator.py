# evaluator.py
import time
import json
import asyncio
from agents import Orchestrator
from memory import load_memory


# ------------------------------
# Load topic DB
# ------------------------------
with open("sample_content.json", "r") as f:
    TOPIC_DB = json.load(f)

orch = Orchestrator(TOPIC_DB, use_llm=False)


# ------------------------------
# Metrics storage
# ------------------------------
metrics = {
    "diagnosis_time": 0,
    "explanation_time": 0,
    "practice_time": 0,
    "questions_generated": 0,
    "correctness_checks": 0,
    "performance_memory_after": None
}


async def evaluate_topic(user_id: str, topic: str):
    # --------------------------
    # 1. Evaluate diagnosis
    # --------------------------
    t1 = time.time()
    diag = await orch.handle(user_id, topic, "diagnose")
    t2 = time.time()

    metrics["diagnosis_time"] = round(t2 - t1, 4)
    print(f"[✓] Diagnosis completed in {metrics['diagnosis_time']}s")

    # --------------------------
    # 2. Evaluate explanation
    # --------------------------
    t3 = time.time()
    explanation = await orch.explainer.explain(user_id, topic, level="beginner")
    t4 = time.time()

    metrics["explanation_time"] = round(t4 - t3, 4)
    print(f"[✓] Explanation completed in {metrics['explanation_time']}s")

    # --------------------------
    # 3. Evaluate practice generation
    # --------------------------
    t5 = time.time()
    practice = await orch.practice.generate_practice(user_id, topic, level="beginner")
    t6 = time.time()

    metrics["practice_time"] = round(t6 - t5, 4)
    metrics["questions_generated"] = len(practice["practice"])
    print(f"[✓] Generated {metrics['questions_generated']} practice questions")

    # --------------------------
    # 4. Evaluate grading performance
    # --------------------------
    metrics["correctness_checks"] = 0

    for q in practice["practice"]:
        await orch.feedback.grade(
            user_id,
            topic,
            q["id"],
            q["answer"],
            q["answer"]  # correct answers for eval
        )
        metrics["correctness_checks"] += 1

    print(f"[✓] Performed {metrics['correctness_checks']} grading checks")

    # --------------------------
    # 5. Check memory updates
    # --------------------------
    performance = load_memory(user_id, f"perf_{topic}")
    metrics["performance_memory_after"] = performance

    print("\nFinal memory state:")
    print(performance)


def run_evaluation():
    user_id = "eval_user"
    topic = "binary search"

    print("\n==============================")
    print("   ALCA EVALUATION SCRIPT")
    print("==============================\n")

    asyncio.run(evaluate_topic(user_id, topic))

    print("\n==============================")
    print("        FINAL METRICS")
    print("==============================\n")

    for k, v in metrics.items():
        print(f"- {k}: {v}")


if __name__ == "__main__":
    run_evaluation()