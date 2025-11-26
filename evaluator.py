"""
evaluator.py

Usage (from project root, with venv activated):

(venv) PS E:\alca> python evaluator.py E:\alca\sample_content_expanded.json

Outputs:
 - evaluation_report.json  (saved in project root)
 - Console summary of key metrics

Notes:
 - Requires agents.py and memory.py to be present and importable from project root.
 - Uses a lightweight string-similarity grader (difflib) to simulate semantic grading.
"""

import json
import time
import random
import difflib
import statistics
from pathlib import Path

# Try to import your orchestrator/agents and memory manager.
# If you used different class names, update these imports accordingly.
try:
    # Orchestrator in earlier instructions exposes Orchestrator class with handle() and grade_answer()
    from agents import Orchestrator
    from memory import MemoryManager
except Exception as e:
    # If imports fail, we still provide a fallback evaluator that analyzes dataset-only metrics.
    Orchestrator = None
    MemoryManager = None
    print("Warning: Could not import Orchestrator or MemoryManager from local files.", e)
    print("Evaluator will run a dataset-only pass (no agent runtime).")


def similarity_score(a: str, b: str) -> float:
    """Return a 0..1 similarity score between two strings (difflib SequenceMatcher)."""
    if a is None or b is None:
        return 0.0
    return difflib.SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio()


def grade_answer(student_answer: str, correct_answer: str, threshold: float = 0.8) -> dict:
    """
    Grade using exact match + similarity.
    Returns dict with boolean and numeric score.
    """
    if student_answer is None:
        student_answer = ""
    if correct_answer is None:
        correct_answer = ""

    # exact match (case-insensitive)
    if student_answer.strip().lower() == correct_answer.strip().lower():
        return {"correct": True, "score": 1.0}

    # similarity fallback
    score = similarity_score(student_answer, correct_answer)
    return {"correct": score >= threshold, "score": score}


def evaluate_with_agents(content: dict, runs_per_topic: int = 5, user_prefix: str = "auto_user") -> dict:
    """
    If Orchestrator is available, run the agent pipeline.
    For each topic:
      - run diagnosis (measure latency)
      - run explanation (measure latency)
      - run practice: ask `runs_per_topic` practice q's, grade them (use real correct answers)
    """
    memory = MemoryManager() if MemoryManager else None
    orch = Orchestrator(content, memory) if Orchestrator and MemoryManager else None

    report = {
        "timestamp": time.time(),
        "topics": {}
    }

    for topic in content.keys():
        stats = {
            "diagnosis_times": [],
            "explanation_times": [],
            "practice_times": [],
            "practice_scores": [],
            "num_questions": 0
        }

        # single diagnostic & explanation pass (timed)
        user_id = f"{user_prefix}_{topic.replace(' ', '_')}_{random.randint(1,9999)}"

        if orch:
            start = time.perf_counter()
            diag = orch.handle(user_id, topic, "diagnose")
            elapsed = time.perf_counter() - start
            stats["diagnosis_times"].append(elapsed)

            start = time.perf_counter()
            learn = orch.handle(user_id, topic, "learn")
            elapsed = time.perf_counter() - start
            stats["explanation_times"].append(elapsed)
        else:
            # simulated timings for non-agent mode
            stats["diagnosis_times"].append(random.uniform(0.01, 0.05))
            stats["explanation_times"].append(random.uniform(0.01, 0.1))

        # practice runs
        for i in range(runs_per_topic):
            if orch:
                start = time.perf_counter()
                prac = orch.handle(user_id, topic, "practice")
                elapsed = time.perf_counter() - start
            else:
                # simulated pick
                prac_questions = content[topic].get("practice", [])
                if not prac_questions:
                    continue
                prac = {"question": random.choice(prac_questions), "difficulty": prac_questions[0].get("difficulty", "beginner")}
                elapsed = random.uniform(0.01, 0.1)

            stats["practice_times"].append(elapsed)
            stats["num_questions"] += 1

            # grade using provided correct answer (simulate a student by using the correct answer 60% of the time + noise)
            correct_answer = None
            student_answer = None
            if isinstance(prac, dict):
                q = prac.get("question") or prac.get("question", None)  # handle both formats
                # If q is nested dict (our agents return question as dict), handle accordingly
                if isinstance(q, dict):
                    correct_answer = q.get("answer")
                    qid = q.get("id")
                    question_text = q.get("question")
                else:
                    # prac may be the question dict itself
                    question_text = prac.get("question")
                    correct_answer = prac.get("answer")
                    qid = prac.get("id")

            # Simulate student answer: 0.6 chance correct, else produce similar or random answer
            if random.random() < 0.6:
                student_answer = correct_answer
            else:
                # produce a noisy answer by shuffling words or trimming
                if isinstance(correct_answer, str) and " " in correct_answer:
                    parts = correct_answer.split()
                    random.shuffle(parts)
                    student_answer = " ".join(parts[: max(1, len(parts)//2)])
                else:
                    student_answer = correct_answer  # fallback

            grade = grade_answer(student_answer or "", correct_answer or "")
            stats["practice_scores"].append(grade["score"])

            # If orch available, notify memory via grade API (keeps stats consistent)
            if orch:
                try:
                    orch.grade_answer(user_id, topic, qid, student_answer or "", correct_answer or "")
                except Exception:
                    # ignore memory update errors during automated run
                    pass

        # summarise topic
        topic_report = {
            "diagnosis_latency_ms": round(statistics.mean(stats["diagnosis_times"]) * 1000, 2) if stats["diagnosis_times"] else None,
            "explanation_latency_ms": round(statistics.mean(stats["explanation_times"]) * 1000, 2) if stats["explanation_times"] else None,
            "practice_latency_ms": round(statistics.mean(stats["practice_times"]) * 1000, 2) if stats["practice_times"] else None,
            "num_practice_questions": stats["num_questions"],
            "average_practice_score": round(statistics.mean(stats["practice_scores"]), 4) if stats["practice_scores"] else None,
        }

        report["topics"][topic] = topic_report

    # Aggregate metrics
    all_practice_scores = [report["topics"][t]["average_practice_score"] for t in report["topics"] if report["topics"][t]["average_practice_score"] is not None]
    report["summary"] = {
        "num_topics": len(report["topics"]),
        "avg_practice_score_overall": round(statistics.mean(all_practice_scores), 4) if all_practice_scores else None,
        "timestamp": time.time()
    }

    return report


def dataset_only_stats(content: dict) -> dict:
    """Produce a lightweight dataset-only report (counts, questions per topic)."""
    r = {"topics": {}, "timestamp": time.time()}
    for tname, tdata in content.items():
        dcount = len(tdata.get("diagnostic", []))
        pcount = len(tdata.get("practice", []))
        r["topics"][tname] = {"diagnostic_count": dcount, "practice_count": pcount}
    r["summary"] = {
        "num_topics": len(r["topics"]),
        "total_diagnostic": sum(v["diagnostic_count"] for v in r["topics"].values()),
        "total_practice": sum(v["practice_count"] for v in r["topics"].values())
    }
    return r


def main(content_path: str):
    p = Path(content_path)
    if not p.exists():
        print(f"ERROR: dataset file not found: {content_path}")
        return

    content = json.loads(p.read_text(encoding="utf-8"))

    print("Running evaluator on:", content_path)
    print("Topics found:", len(content))

    if Orchestrator and MemoryManager:
        print("Orchestrator and Memory detected: running agent-driven evaluation.")
        report = evaluate_with_agents(content, runs_per_topic=5)
    else:
        print("Agents not available — running dataset-only stats.")
        report = dataset_only_stats(content)

    # Save report
    out_path = Path("evaluation_report.json")
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nSaved evaluation report to: {out_path.resolve()}\n")

    # Print summary
    if "summary" in report:
        print("Summary:")
        for k, v in report["summary"].items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python evaluator.py <path-to-sample_content_expanded.json>")
    else:
        main(sys.argv[1])
