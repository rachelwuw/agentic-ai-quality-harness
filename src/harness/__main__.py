import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from .agent import run_agent
from .client import LocalClient
from .evaluate import evaluate

ROOT = Path(__file__).resolve().parents[2]

def main():
    parser = argparse.ArgumentParser(description="Rachel's local agent quality harness")
    parser.add_argument("command", choices=["doctor", "run", "eval"])
    parser.add_argument("prompt", nargs="?", default="Run the login mock suite and summarize its result.")
    parser.add_argument("--cases", default=str(ROOT / "evals/cases.json"))
    parser.add_argument("--output", default="reports/latest.json")
    args = parser.parse_args()
    try:
        client = LocalClient()
        if args.command == "doctor":
            print(json.dumps(client.models(), indent=2))
            return 0
        result = run_agent(args.prompt, client) if args.command == "run" else evaluate(args.cases, client)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps({"recorded_at": datetime.now(timezone.utc).isoformat(), "model": client.model, "base_url": client.base, **result}, indent=2, ensure_ascii=False))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"Saved: {output}")
        return int(result["status"] != "completed") if args.command == "run" else int(result["passed"] != result["total"])
    except Exception as exc:
        print(f"Error: {exc}. Check LM Studio server, model identifier, and README.", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
