# demo_cli.py
import json
import asyncio
from agents import Orchestrator
from memory import load_memory, get_history

# Load topic content
with open("sample_content.json", "r") as f:
    TOPIC_DB = json.load(f)

orch = Orchestrator(TOPIC_DB, use_llm=False)


def print_header(text):
    print("\n" + "=" * 50)
    print(text)
    print("=" * 50)


async def full_learning_session(user_id: str, topic: str):
    print_header("STEP 1 — DIAGNOSE")
    diag = await orch.handle(user_id, topic, "diagnose")
    print("Diagnostic questions:")
    for q in diag["diagnostic"]:
        print(" -", q["question"])

    level = diag["estimated_level"] or "beginner"
    print("\nEstimated level:", level)

    print_header("STEP 2 — EXPLANATION + PRACTICE")
    out = await orch.handle(user_id, topic, "learn")

    print("\nExplanation:")
    print(out["explanation"]["explanation"])

    print("\nPractice Questions:")
    for i, q in enumerate(out["practice"]["practice"], 1):
        print(f"\nQ{i}.", q["question"])
        ans = input("Your answer: ")

        # Grade answer
        grade = await orch.feedback.grade(
            user_id,
            topic,
            q["id"],
            ans,
            q["answer"]
        )

        if grade["correct"]:
            print("✔ Correct!")
        else:
            print("✘ Incorrect. Correct answer:", grade["expected"])

    print_header("STEP 3 — YOUR MEMORY")
    perf = load_memory(user_id, f"perf_{topic}")
    history = get_history(user_id)

    print("\nPerformance:", perf)
    print("\nRecent session logs:")
    for h in history[-5:]:
        print(f"[{h['action']}] → {h['payload']}")


if __name__ == "__main__":
    user = input("Enter user id: ")
    topic = input("Enter topic (e.g., binary search): ").lower()

    asyncio.run(full_learning_session(user, topic))
