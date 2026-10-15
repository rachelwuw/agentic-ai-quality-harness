"""Opt-in offline interval sidecars; never included in model-facing trace facts."""
import argparse
import hashlib
import json
import os
from pathlib import Path

from .saved_trace import validate_source
from .trace_facts import derive_trace_facts, interval_relationship

RELATIONS_VERSION = "calendar-offline-interval-relations-v1"


def derive_interval_relations(item):
    """Consume legacy saved facts without extending their model-facing schema.

    Flags describe each event independently, not union coverage or availability.
    Missing busy arrays stay null; a recorded empty array is not proof of free.
    """
    facts = derive_trace_facts(item)
    observations = []
    for source in facts["tool_observations"]:
        if source.get("tool_name") != "check_availability":
            continue
        observation = {"event_index": source["event_index"],
                       "reported_available": source.get("reported_available"),
                       "issues": list(source["issues"]), "busy_intervals": None}
        observations.append(observation)
        if "busy_intervals" not in source:
            continue
        observation["busy_intervals"] = []
        for event in source["busy_intervals"]:
            query = None if source.get("reported_error") else source.get("query_interval")
            relation = interval_relationship(query, event)
            record = {"busy_index": event["busy_index"], **relation}
            if relation["overlaps_query"] is None:
                record["issue"] = "interval_relationship_unavailable"
            observation["busy_intervals"].append(record)
    return {"version": RELATIONS_VERSION, "source_facts_version": facts["version"],
            "scope": "Offline saved evidence only; per-event relationships, not union coverage "
                     "or independently verified availability. Not model input.",
            "issues": list(facts["issues"]), "tool_observations": observations}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True, help="New sidecar path; existing files are refused")
    args = parser.parse_args(argv)
    source_path, output = Path(args.input), Path(args.output)
    if source_path.resolve() == output.resolve():
        parser.error("Sidecar must not overwrite the source")
    raw = source_path.read_bytes()
    try:
        items = validate_source(json.loads(raw))
    except (ValueError, TypeError) as error:
        parser.error(str(error))
    report = {"version": RELATIONS_VERSION, "source_sha256": hashlib.sha256(raw).hexdigest(),
              "results": [{"id": item["id"], **derive_interval_relations(item)} for item in items]}
    output.parent.mkdir(parents=True, exist_ok=True)
    # Private traces may be analyzed locally; never overwrite historical evidence.
    with open(output, "x", encoding="utf-8", opener=lambda path, flags: os.open(path, flags, 0o600)) as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
