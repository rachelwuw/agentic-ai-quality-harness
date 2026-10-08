"""Malformed evidence must be diagnosed without invoking real dependencies."""
import copy
import json
import re
from pathlib import Path
import pytest
from harness.saved_trace import validate_case, validate_source
from harness.trace_facts import derive_trace_facts
from harness.calendar_judge import review, parse_verdict, main


def case():
    return {"id": "broken-case", "prompt": "Check availability", "structural_pass": True,
            "api_calls": [{}], "run": {"status": "completed", "answer": "Busy", "events": []},
            "answer_review": {"criteria": ["No Google API request may occur", "Truthful answer"],
                              "forbidden_behaviors": []}}


@pytest.mark.parametrize("field,value", [("run", None), ("run", []),
    ("run.events", None), ("run.events", [None]), ("run.events", [{}]),
    ("run.answer", 17), ("prompt", None), ("answer_review", []),
    ("answer_review.criteria", [17]), ("api_calls", "not an array")])
def test_case_shape_errors_have_case_and_field_and_do_not_invoke_judge(field, value):
    item = case()
    container = item
    parts = field.split(".")
    for key in parts[:-1]:
        container = container[key]
    container[parts[-1]] = value
    before = copy.deepcopy(item)
    result = review(item, [], lambda _: pytest.fail("Invalid input must not invoke the model"),
                    deterministic_requirements=["No Google API request may occur"], derive_facts=True)
    assert result["status"] == "input_error"
    assert result["error_category"] == "input_format_error"
    assert any(d["field"].startswith(field) and d["case_id"] == "broken-case" for d in result["diagnostics"])
    assert result["computed_trace_facts"]["version"]
    assert item == before
    if field not in ("api_calls", "answer_review", "answer_review.criteria"):
        assert result["checks"][0]["verdict"] == "FAIL"
        assert result["checks"][0]["grader"] == "deterministic_trace"


@pytest.mark.parametrize("result,field", [(None, ".result"), ([], ".result"),
    ({"available": "false"}, ".result.available"),
    ({"busy_intervals": [None]}, ".result.busy_intervals[0]"),
    ({"busy_intervals": [{"start": [], "end": {"dateTime": 12}}]}, ".result.busy_intervals[0].start")])
def test_malformed_tool_results_have_indexed_paths(result, field):
    item = case()
    item["run"]["events"] = [{"type": "tool", "name": "check_availability", "result": result}]
    reviewed = review(item, [], lambda _: pytest.fail(), derive_facts=True)
    assert any(d["field"] == "run.events[0]" + field for d in reviewed["diagnostics"])
    assert reviewed["status"] == "input_error"


@pytest.mark.parametrize("item", [None, [], {"run": None}, {"run": []},
    {"api_calls": [], "run": {"events": [None, {}]}}])
def test_trace_facts_defensively_report_unknown_without_crashing(item):
    facts = derive_trace_facts(item)
    assert facts["issues"]
    if isinstance(item, dict) and item.get("api_calls") == []:
        assert facts["external_request_count"] == 0


def test_missing_api_evidence_and_legitimate_invalid_tool_arguments_stay_reviewable():
    item = case()
    item.pop("api_calls")
    item["run"]["events"] = [{"type": "tool", "name": "check_availability",
                             "arguments": "{invalid JSON", "result": {"error": "invalid_arguments"}}]
    assert validate_case(item) == []
    assert derive_trace_facts(item)["external_request_count"] is None


@pytest.mark.parametrize("source,path", [(None, "input.results"), ({"results": None}, "input.results"),
    ({"results": [None]}, "input.results[0]"),
    ({"results": [{"id": [], "structural_pass": True}]}, "input.results[0].id"),
    ({"results": [{"id": "x", "structural_pass": 1}]}, "input.results[0].structural_pass"),
    ({"results": [case(), case()]}, "input.results[1].id")])
def test_invalid_envelope_is_rejected_with_field(source, path):
    with pytest.raises(ValueError, match=re.escape(path)):
        validate_source(source)


def test_cli_rejects_invalid_envelope_before_runtime_access(tmp_path, monkeypatch):
    source = tmp_path / "bad.json"
    source.write_text('{"results": null}')
    monkeypatch.setenv("JUDGE_MODEL", "judge")
    monkeypatch.setattr("sys.argv", ["judge", "--input", str(source)])
    monkeypatch.setattr("harness.calendar_judge.LocalClient", lambda **_: pytest.fail("No runtime on malformed input"))
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2


@pytest.mark.parametrize("raw", [None, [], '{"checks":[{"id":"c1","verdict":[],"reason":"x","evidence":["x"]}]}'])
def test_bad_output_types_raise_validation_error(raw):
    with pytest.raises(ValueError):
        parse_verdict(raw, ["c1"])


def test_format_failure_transport_failure_and_semantic_uncertain_are_distinct():
    item = case()
    def timeout(_):
        raise TimeoutError()
    malformed = review(item, [], lambda _: "not JSON", deterministic_requirements=["No Google API request may occur"])
    failed = review(item, [], timeout, deterministic_requirements=["No Google API request may occur"])
    def uncertain(messages):
        checks = json.loads(messages[-1]["content"])["checks"]
        return json.dumps({"checks": [{"id": c["id"], "verdict": "UNCERTAIN",
            "reason": "Insufficient semantic evidence", "evidence": ["Unknown claim"]} for c in checks]})
    semantic = review(item, [], uncertain)
    assert malformed["error_category"] == "model_output_error"
    assert malformed["diagnostics"][0]["field"] == "judge.output"
    assert failed["error_category"] == "transport_error"
    assert semantic["status"] == "reviewed" and semantic["verdict"] == "UNCERTAIN"
    for result in (malformed, failed):
        assert result["checks"][0]["verdict"] == "FAIL"
        assert result["verdict"] == "FAIL"


def test_empty_checks_do_not_produce_vacuous_pass():
    item = case()
    item["answer_review"]["criteria"] = []
    result = review(item, [], lambda _: pytest.fail())
    assert result["status"] == "input_error" and result["verdict"] == "UNCERTAIN"


def test_all_saved_development_case_shapes_remain_compatible():
    root = Path(__file__).parents[1]
    paths = list((root / "evals").glob("*.json")) + [root / "reports/baseline/calendar-baseline-v7-retry-20261007.json"]
    count = 0
    for path in paths:
        source = json.loads(path.read_text())
        if not isinstance(source, dict) or "results" not in source:
            continue
        for item in source["results"]:
            if "run" in item and item["run"].get("status") == "completed":
                assert validate_case(item) == [], (path, item.get("id"), validate_case(item))
                count += 1
    assert count >= 15


def test_cli_saves_invalid_case_and_continues_without_losing_trace_evidence(tmp_path, monkeypatch):
    root = Path(__file__).parents[1]
    bad, good = case(), case()
    good["id"] = "valid-case"
    bad["run"]["events"] = [None]
    source, output = tmp_path / "source.json", tmp_path / "report.json"
    source.write_text(json.dumps({"model": "sut", "results": [bad, good]}))
    monkeypatch.setenv("JUDGE_MODEL", "judge")
    monkeypatch.setattr("sys.argv", ["judge", "--input", str(source), "--output", str(output),
                                    "--rubric", str(root / "evals/calendar_judge_rubric_v10.json")])
    class Client:
        base = "http://127.0.0.1:1234/v1"
        def __init__(self, model, timeout):
            self.model = model
        def models(self):
            return {"data": [{"id": "judge"}]}
        def request(self, path, payload):
            data = json.loads(payload["messages"][-1]["content"])
            assert data["tool_events"] == []  # only good case reaches this stub
            raw = json.dumps({"checks": [{"id": c["id"], "verdict": "PASS", "reason": "Supported",
                                         "evidence": ["Busy"]} for c in data["checks"]]})
            return {"choices": [{"finish_reason": "stop", "message": {"content": raw}}]}
    monkeypatch.setattr("harness.calendar_judge.LocalClient", Client)
    assert main() == 1
    report = json.loads(output.read_text())
    assert report["state"] == "completed"
    assert [x["status"] for x in report["results"]] == ["input_error", "reviewed"]
    assert report["results"][0]["checks"][0]["grader"] == "deterministic_trace"
    assert report["results"][0]["checks"][0]["verdict"] == "FAIL"
    assert report["results"][0]["diagnostics"][0]["field"] == "run.events[0]"
    assert json.loads(source.read_text())["results"][0] == bad
