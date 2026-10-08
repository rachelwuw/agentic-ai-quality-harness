"""Deterministic facts derived from saved Calendar traces, never from answers."""
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

FACTS_VERSION = "calendar-trace-facts-v1"


def interval(start, end, target=None):
    """Require explicit offsets; never guess a timezone for naive timestamps."""
    first, last = datetime.fromisoformat(start), datetime.fromisoformat(end)
    if first.utcoffset() is None or last.utcoffset() is None:
        raise ValueError("missing_offset")
    if last <= first:
        raise ValueError("invalid_interval")
    def rendered(value, zone):
        local = value.astimezone(zone)
        return {"datetime": local.isoformat(), "timezone_label": local.tzname()}
    result = {"utc_start": first.astimezone(timezone.utc).isoformat(),
              "utc_end": last.astimezone(timezone.utc).isoformat()}
    if target is not None:
        zone = ZoneInfo(target)
        result["in_query_timezone"] = {"time_zone": target,
            "start": rendered(first, zone), "end": rendered(last, zone)}
    return result


def derive_trace_facts(item):
    facts = {"version": FACTS_VERSION, "provenance": "derived_from_saved_trace",
             "scope": "Recorded tool evidence only; controlled requests may be simulated. "
                      "No independent network verification or answer interpretation.",
             "external_request_count": None, "tool_observations": [], "issues": []}
    calls = item.get("api_calls")
    if isinstance(calls, list) and all(isinstance(c, dict) for c in calls):
        facts["external_request_count"] = len(calls)
    else:
        facts["issues"].append("external_request_trace_missing_or_malformed")
    events = item.get("run", {}).get("events")
    if not isinstance(events, list):
        facts["issues"].append("tool_event_trace_missing_or_malformed")
        return facts
    for index, event in enumerate(events):
        if not isinstance(event, dict) or event.get("type") != "tool":
            continue
        observation = {"event_index": index, "tool_name": event.get("name"), "issues": []}
        facts["tool_observations"].append(observation)
        result = event.get("result")
        if not isinstance(result, dict):
            observation["issues"].append("tool_result_missing_or_malformed")
            continue
        if event.get("name") != "check_availability":
            continue
        observation["reported_available"] = result.get("available") if isinstance(result.get("available"), bool) else None
        if isinstance(result.get("error"), str):
            observation["reported_error"] = result["error"]
        target = result.get("time_zone")
        if not target:
            try:
                args = event.get("arguments")
                args = json.loads(args) if isinstance(args, str) else args
                target = args.get("time_zone") if isinstance(args, dict) else None
            except (ValueError, TypeError):
                target = None
        try:
            if not isinstance(target, str):
                raise ValueError("missing_zone")
            ZoneInfo(target)
        except (ValueError, ZoneInfoNotFoundError):
            observation["issues"].append("query_timezone_missing_or_invalid")
            target = None
        query = None
        try:
            query = interval(result["start"], result["end"], target)
            observation["query_interval"] = query
        except (KeyError, ValueError, TypeError):
            observation["issues"].append("query_interval_unavailable")
        busy = result.get("busy_intervals")
        if not isinstance(busy, list):
            observation["issues"].append("busy_intervals_missing_or_malformed")
            continue
        observation["busy_intervals"] = []
        for busy_index, entry in enumerate(busy):
            record = {"busy_index": busy_index}
            try:
                converted = interval(entry["start"]["dateTime"], entry["end"]["dateTime"], target)
                record.update(converted)
                if query is not None:
                    record["overlaps_query"] = (datetime.fromisoformat(converted["utc_start"]) < datetime.fromisoformat(query["utc_end"]) and
                                                 datetime.fromisoformat(converted["utc_end"]) > datetime.fromisoformat(query["utc_start"]))
            except (KeyError, ValueError, TypeError):
                record["issue"] = "busy_interval_unavailable_or_all_day"
            observation["busy_intervals"].append(record)
    return facts
