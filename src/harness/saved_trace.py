"""Shape validation for untrusted saved evidence; no model or network access."""


def validate_source(source):
    """Validate the envelope before selecting cases or contacting a runtime."""
    if not isinstance(source, dict) or not isinstance(source.get("results"), list):
        raise ValueError("input.results: expected an array in an object")
    seen = set()
    for index, item in enumerate(source["results"]):
        field = f"input.results[{index}]"
        if not isinstance(item, dict):
            raise ValueError(field + ": expected an object")
        ident = item.get("id")
        if not isinstance(ident, str) or not ident.strip():
            raise ValueError(field + ".id: expected a nonempty string")
        if ident in seen:
            raise ValueError(field + ".id: duplicate case id")
        seen.add(ident)
        if not isinstance(item.get("structural_pass"), bool):
            raise ValueError(field + ".structural_pass: expected a boolean")
    return source["results"]


def validate_case(item):
    """Return field diagnostics; missing API evidence remains explicitly unknown.

    Tool arguments may contain invalid JSON: that is legitimate SUT evidence.
    Tool errors/all-day events and extra historical fields are preserved.
    """
    issues = []
    ident = item.get("id", "<unknown>") if isinstance(item, dict) else "<unknown>"
    def issue(field, expected):
        issues.append({"case_id": ident, "field": field, "expected": expected})
    def text(value, field):
        if not isinstance(value, str) or not value.strip():
            issue(field, "nonempty string")
    def strings(value, field):
        if not isinstance(value, (list, tuple)):
            issue(field, "array of nonempty strings")
        else:
            for index, entry in enumerate(value):
                text(entry, f"{field}[{index}]")
    if not isinstance(item, dict):
        issue("case", "object")
        return issues
    text(item.get("prompt"), "prompt")
    run = item.get("run")
    if not isinstance(run, dict):
        issue("run", "object")
    else:
        text(run.get("status"), "run.status")
        if run.get("status") == "completed":
            text(run.get("answer"), "run.answer")
        events = run.get("events")
        if not isinstance(events, list):
            issue("run.events", "array")
        else:
            for index, event in enumerate(events):
                field = f"run.events[{index}]"
                if not isinstance(event, dict):
                    issue(field, "object")
                    continue
                text(event.get("type"), field + ".type")
                if event.get("type") != "tool":
                    continue
                text(event.get("name"), field + ".name")
                if "arguments" in event and not isinstance(event["arguments"], (str, dict)):
                    issue(field + ".arguments", "string or object")
                result = event.get("result")
                if not isinstance(result, dict):
                    issue(field + ".result", "object")
                    continue
                if event.get("name") != "check_availability":
                    continue
                for key in ("start", "end", "time_zone", "error"):
                    if key in result:
                        text(result[key], field + ".result." + key)
                if result.get("available") is not None and not isinstance(result["available"], bool):
                    issue(field + ".result.available", "boolean or unknown/null")
                if "busy_intervals" in result:
                    busy = result["busy_intervals"]
                    if not isinstance(busy, list):
                        issue(field + ".result.busy_intervals", "array")
                    else:
                        for n, entry in enumerate(busy):
                            path = field + f".result.busy_intervals[{n}]"
                            if not isinstance(entry, dict):
                                issue(path, "object")
                                continue
                            for endpoint in ("start", "end"):
                                value = entry.get(endpoint)
                                if not isinstance(value, dict):
                                    issue(path + "." + endpoint, "dateTime/date object")
                                elif not any(k in value for k in ("dateTime", "date")):
                                    issue(path + "." + endpoint, "dateTime/date object")
                                else:
                                    for key in ("dateTime", "date"):
                                        if key in value:
                                            text(value[key], path + "." + endpoint + "." + key)
    rubric = item.get("answer_review")
    if not isinstance(rubric, dict):
        issue("answer_review", "object")
    else:
        strings(rubric.get("criteria"), "answer_review.criteria")
        strings(rubric.get("forbidden_behaviors"), "answer_review.forbidden_behaviors")
    calls = item.get("api_calls")
    if calls is not None:
        if not isinstance(calls, list):
            issue("api_calls", "array of objects or missing/unknown")
        else:
            for index, call in enumerate(calls):
                if not isinstance(call, dict):
                    issue(f"api_calls[{index}]", "object")
    return issues
