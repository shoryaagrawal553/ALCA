import json
import time
import random
import difflib
import statistics
from pathlib import Path

try:
    from agents import Orchestrator
    from memory import MemoryManager
except Exception:
    Orchestrator = None
    MemoryManager = None


def evaluate_answer(student_answer: str, correct_answer: str) -> bool:
    """Simple exact match check (lowercased)."""
    if not isinstance(student_answer, str):
        student_answer = ""
    if not isinstance(correct_answer, str):
        correct_answer = ""
    return student_answer.strip().lower() == correct_answer.strip().lower()


# ------------------------------
# Internal similarity scorer
# ------------------------------
def similarity_score(a: str, b: str) -> float:
    if a is None or b is None:
        return 0.0
    return difflib.SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio()


def grade(student_answer: str, correct_answer: str, threshold: float = 0.8) -> dict:
    if student_answer.strip().lower() == correct_answer.strip().lower():
        return {"correct": True, "score": 1.0}
    score = similarity_score(student_answer, correct_answer)
    return {"correct": score >= threshold, "score": score}


# ------------------------------
# Evaluator CLASS 
# ------------------------------
class Evaluator:
    def __init__(self, runs_per_topic: int = 5):
        self.runs_per_topic = runs_per_topic

    def run_full_evaluation(self, content_file: str = "sample_content_expanded.json") -> dict:
        """Full evaluation used by /api/evaluate"""
        p = Path(content_file)
        if not p.exists():
            return {"error": f"Dataset not found: {content_file}"}

        content = json.loads(p.read_text(encoding="utf-8"))

        if Orchestrator and MemoryManager:
            return self._evaluate_with_agents(content)
        else:
            return self._dataset_only_stats(content)

    # ---------------------------------------------------------
    # agent-driven evaluation
    # ---------------------------------------------------------
    def _evaluate_with_agents(self, content: dict) -> dict:
        memory = MemoryManager()
        orch = Orchestrator(content, memory)

        report = {"timestamp": time.time(), "topics": {}}

        for topic in content.keys():
            user_id = f"eval_{topic}_{random.randint(1,9999)}"

            # measure timings
            diag_t = self._time(lambda: orch.handle(user_id, topic, "diagnose"))
            exp_t = self._time(lambda: orch.handle(user_id, topic, "learn"))

            # practice
            practice_times = []
            practice_scores = []
            num_questions = 0

            for _ in range(self.runs_per_topic):
                t = self._time(lambda: orch.handle(user_id, topic, "practice"))
                practice_times.append(t)

                prac = orch.handle(user_id, topic, "practice")
                q = prac.get("question")
                if isinstance(q, dict):
                    ans = q.get("answer")
                    qid = q.get("id")
                else:
                    continue

                # simulate:
                student_answer = ans if random.random() < 0.6 else ans[::-1]
                g = grade(student_answer, ans)
                practice_scores.append(g["score"])
                num_questions += 1

                try:
                    orch.grade_answer(user_id, topic, qid, student_answer, ans)
                except:
                    pass

            report["topics"][topic] = {
                "diagnosis_latency_ms": round(diag_t * 1000, 2),
                "explanation_latency_ms": round(exp_t * 1000, 2),
                "practice_latency_ms": round(statistics.mean(practice_times) * 1000, 2)
                if practice_times else None,
                "num_practice_questions": num_questions,
                "average_practice_score": round(statistics.mean(practice_scores), 4)
                if practice_scores else None,
            }

        all_scores = [
            report["topics"][t]["average_practice_score"]
            for t in report["topics"]
            if report["topics"][t]["average_practice_score"] is not None
        ]

        report["summary"] = {
            "num_topics": len(content),
            "avg_practice_score_overall": round(statistics.mean(all_scores), 4)
            if all_scores else None,
            "timestamp": time.time(),
        }

        return report

    # ---------------------------------------------------------
    # dataset-only evaluation
    # ---------------------------------------------------------
    def _dataset_only_stats(self, content: dict) -> dict:
        r = {"topics": {}, "timestamp": time.time()}
        for tname, tdata in content.items():
            r["topics"][tname] = {
                "diagnostic_count": len(tdata.get("diagnostic", [])),
                "practice_count": len(tdata.get("practice", [])),
            }

        r["summary"] = {
            "num_topics": len(r["topics"]),
            "total_diagnostic": sum(v["diagnostic_count"] for v in r["topics"].values()),
            "total_practice": sum(v["practice_count"] for v in r["topics"].values()),
        }
        return r

    # ---------------------------------------------------------
    # timing helper
    # ---------------------------------------------------------
    @staticmethod
    def _time(fn):
        start = time.perf_counter()
        fn()
        return time.perf_counter() - start


# ------------------------------
# CLI entry 
# ------------------------------
def main(content_path: str):
    p = Path(content_path)
    if not p.exists():
        print(f"ERROR: dataset file not found: {content_path}")
        return

    content = json.loads(p.read_text(encoding="utf-8"))

    E = Evaluator()

    print("Running evaluator on:", content_path)
    print("Topics found:", len(content))

    report = E.run_full_evaluation(content_path)

    out_path = Path("evaluation_report.json")
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nSaved evaluation_report.json\n")

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
