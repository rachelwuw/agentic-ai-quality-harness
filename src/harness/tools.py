"""Two in-memory mocks. No shell, Jira, or real test execution."""
import json

REQUIREMENTS = {
    "REQ-1": {"title": "Login", "acceptance": "Valid credentials succeed; invalid credentials fail."},
    "REQ-2": {"title": "Password reset", "acceptance": "Reset link expires after 15 minutes."},
}
SUITES = {
    "login": {"passed": 3, "failed": 0, "failures": []},
    "reset": {"passed": 2, "failed": 1, "failures": ["expired_reset_link_accepted"]},
}

def definition(name, description, key, values):
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": {key: {"type": "string", **({"enum": values} if values else {})}},
                       "required": [key], "additionalProperties": False}}}

TOOLS = [
    definition("get_requirement", "Read a mock requirement; unknown IDs return not_found.", "requirement_id", []),
    definition("run_test_suite", "Return a SIMULATED test result, not real pytest execution.", "suite", list(SUITES)),
]

def execute(name, arguments):
    try:
        args = json.loads(arguments)
    except (ValueError, TypeError):
        return {"error": "invalid_json"}
    registry = {"get_requirement": ("requirement_id", REQUIREMENTS), "run_test_suite": ("suite", SUITES)}
    if name not in registry:
        return {"error": "unknown_tool"}
    key, records = registry[name]
    if not isinstance(args, dict) or set(args) != {key} or not isinstance(args[key], str):
        return {"error": "invalid_arguments"}
    if args[key] not in records:
        return {"error": "not_found", key: args[key]}
    return {key: args[key], "mock": True, **records[args[key]]}
