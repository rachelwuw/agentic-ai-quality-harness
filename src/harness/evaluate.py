"""Transparent starter graders; not a semantic judge or proof of correctness."""
import json
from pathlib import Path
from .agent import run_agent

def grade(case, run):
    tools = [event for event in run["events"] if event["type"] == "tool"]
    actual = [{"name": e["name"], "arguments": json.loads(e["arguments"])} for e in tools]
    text = run["answer"].lower()
    checks = {
        "completed": run["status"] == "completed",
        "tool_sequence": actual == case["expected_calls"],
        "answer_markers": all(marker.lower() in text for marker in case["answer_contains"]),
        "no_forbidden_markers": all(marker.lower() not in text for marker in case.get("answer_excludes", [])),
    }
    return {"passed": all(checks.values()), "checks": checks}

def evaluate(path, complete):
    cases = json.loads(Path(path).read_text())
    results = []
    for case in cases:
        try:
            run = run_agent(case["prompt"], complete)
            verdict = grade(case, run)
            results.append({"id": case["id"], **verdict, "run": run})
        except Exception as exc:
            results.append({"id": case["id"], "passed": False, "error": str(exc)})
    return {"total": len(results), "passed": sum(r["passed"] for r in results), "results": results}
