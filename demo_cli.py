import json
from memory import MemoryManager
from agents import Orchestrator

def run_session():
    print("\n==================================================")
    print("      ALCA — Adaptive Learning CLI Demo")
    print("==================================================\n")

    memory = MemoryManager()

    user_id = input("Enter your user ID: ").strip()
    with open("sample_content_expanded.json", "r", encoding="utf-8") as f:
        content = json.load(f)

    topics = list(content.keys())

    print("Available Topics:")
    for i, t in enumerate(topics, 1):
        print(f"{i}. {t.ljust(15)}")

    choice = int(input("\nEnter topic number: "))
    topic = topics[choice - 1]

    print(f"\nYou selected topic: {topic}\n")

    orch = Orchestrator(content, memory)

    # -----------------------------------------
    # Diagnostic
    # -----------------------------------------
    diag = orch.handle(user_id, topic, "diagnose")
    q = diag["question"]
    print("Diagnostic Question:")
    print(f"Q: {q['question']}")
    _ = input("Your answer (press Enter to continue): ")

    print("\n✔ Diagnostic complete.\n")

    # -----------------------------------------
    # Explanation
    # -----------------------------------------
    learn = orch.handle(user_id, topic, "learn")
    print("Explanation:")
    print(f"Level: {learn['level']}")
    print(learn["explanation"])

    print("\n✔ Explanation complete.\n")

    # -----------------------------------------
    # Practice
    # -----------------------------------------
    prac = orch.handle(user_id, topic, "practice")
    pq = prac["question"]

    print("Practice Question:")
    print(f"(Difficulty: {prac['difficulty']})")
    print(f"Q: {pq['question']}")
    ans = input("Your answer: ")

    # grading
    feedback = orch.grade_answer(user_id, topic, pq["id"], ans, pq["answer"])

    print("\nGrading Result:")
    print(f"Correct answer: {pq['answer']}")
    print(f"Your answer: {ans}")
    print(f"Result: {'✔ Correct' if feedback['correct'] else '✘ Incorrect'}")

    # -----------------------------------------
    # Summary (FIXED HERE)
    # -----------------------------------------
    stats = memory.get_user_summary(user_id)

    print("\n Your Learning Summary:")
    if topic in stats["topics"]:
        t = stats["topics"][topic]
        print(f"Topic: {topic}")
        print(f"Attempts: {t['attempts']}")
        print(f"Correct: {t['correct']}")
        print(f"Accuracy: {t['accuracy']}%")
    else:
        print("No stats available.")

    print("\n==================================================")
    print("              End of Demo Session")
    print("==================================================\n")


if __name__ == "__main__":
    run_session()
