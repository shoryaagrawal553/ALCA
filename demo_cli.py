import json
from agents import Orchestrator
from memory import MemoryManager


def print_banner():
    print("\n" + "=" * 50)
    print("      ALCA — Adaptive Learning CLI Demo")
    print("=" * 50 + "\n")


def choose_topic(db):
    print("Available Topics:")
    topics = list(db.keys())

    for i, t in enumerate(topics, start=1):
        print(f"{i}. {t}")

    while True:
        try:
            choice = int(input("\nEnter topic number: "))
            if 1 <= choice <= len(topics):
                return topics[choice - 1]
        except:
            pass

        print("Invalid choice. Try again.")


def run_session():
    print_banner()

    # Load expanded dataset
    with open("sample_content_expanded.json", "r") as f:
        DB = json.load(f)

    memory = MemoryManager()
    orch = Orchestrator(DB, memory)

    user_id = input("Enter your user ID: ").strip()

    topic = choose_topic(DB)
    print(f"\nYou selected topic: {topic}\n")

    # -----------------------
    # 1) DIAGNOSTIC QUESTION
    # -----------------------
    print("🧠 Diagnostic Question:")
    diag = orch.handle(user_id, topic, "diagnose")
    dq = diag["question"]
    print("Q:", dq["question"])
    input("Your answer (press Enter to continue): ")

    print("\n✔ Diagnostic complete.\n")

    # -----------------------
    # 2) EXPLANATION
    # -----------------------
    print("📘 Explanation:")
    expl = orch.handle(user_id, topic, "learn")
    print(f"Level: {expl['level']}")
    print(expl["explanation"])

    print("\n✔ Explanation complete.\n")

    # -----------------------
    # 3) PRACTICE
    # -----------------------
    print("📝 Practice Question:")
    prac = orch.handle(user_id, topic, "practice")
    pq = prac["question"]

    print(f"(Difficulty: {prac['difficulty']})")
    print("Q:", pq["question"])
    student_ans = input("Your answer: ").strip()

    # -----------------------
    # 4) GRADE ANSWER
    # -----------------------
    result = orch.grade_answer(
        user_id,
        topic,
        pq["id"],
        student_ans,
        pq["answer"]
    )

    print("\n🎯 Grading Result:")
    print("Correct answer:", result["correct_answer"])
    print("Your answer:", result["student_answer"])
    print("Result:", "✔ Correct" if result["correct"] else "✘ Incorrect")

    # -----------------------
    # 5) MEMORY SUMMARY
    # -----------------------
    stats = memory.get_user(user_id)

    print("\n🧾 Your Learning Stats:")
    print(json.dumps(stats, indent=2))

    print("\nSession complete. Goodbye!\n")


if __name__ == "__main__":
    run_session()
