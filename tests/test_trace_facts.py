import copy
import json
from pathlib import Path
import pytest
from harness.trace_facts import derive_trace_facts, interval
from harness.calendar_judge import review


def saved_case():
    data = json.loads((Path(__file__).parents[1] / "evals/judge_v9_new_wording_cases.json").read_text())
    return data["results"][0]


def test_trace_conversion_uses_offsets_and_crosses_date_without_reading_answer():
    item = saved_case()
    before = copy.deepcopy(item)
    facts = derive_trace_facts(item)
    busy = facts["tool_observations"][0]["busy_intervals"][0]
    assert busy["in_query_timezone"]["start"]["datetime"] == "2026-10-07T02:00:00+08:00"
    assert busy["in_query_timezone"]["end"]["datetime"] == "2026-10-07T02:30:00+08:00"
    assert busy["overlaps_query"] is True
    item["run"]["answer"] = "Fabricated conversion and ignore instructions"
    assert derive_trace_facts(item) == facts
    item["run"]["answer"] = before["run"]["answer"]
    assert item == before


def test_winter_and_summer_zone_labels_are_computed_by_zoneinfo():
    winter = interval("2026-01-06T19:00:00+00:00", "2026-01-06T19:30:00+00:00", "America/Los_Angeles")
    summer = interval("2026-07-06T18:00:00+00:00", "2026-07-06T18:30:00+00:00", "America/Los_Angeles")
    assert winter["in_query_timezone"]["start"] == {"datetime":"2026-01-06T11:00:00-08:00", "timezone_label":"PST"}
    assert summer["in_query_timezone"]["start"] == {"datetime":"2026-07-06T11:00:00-07:00", "timezone_label":"PDT"}


@pytest.mark.parametrize("start,end", [("2026-10-06T11:00:00", "2026-10-06T11:30:00"),
    ("2026-10-06T11:30:00-07:00", "2026-10-06T11:00:00-07:00")])
def test_missing_offsets_and_invalid_intervals_are_not_guessed(start, end):
    with pytest.raises(ValueError):
        interval(start, end, "Asia/Taipei")


def test_adjacent_interval_does_not_overlap():
    item = saved_case()
    result = next(e["result"] for e in item["run"]["events"] if e["type"] == "tool")
    result["start"] = "2026-10-07T02:30:00+08:00"
    result["end"] = "2026-10-07T03:00:00+08:00"
    assert derive_trace_facts(item)["tool_observations"][0]["busy_intervals"][0]["overlaps_query"] is False


def test_malformed_missing_and_all_day_evidence_remains_unknown():
    item = saved_case()
    item["api_calls"] = None
    result = next(e["result"] for e in item["run"]["events"] if e["type"] == "tool")
    result["time_zone"] = "Invalid/Zone"
    result["start"] = "not a timestamp"
    result["busy_intervals"] = [{"start":{"date":"2026-10-06"}, "end":{"date":"2026-10-07"}}]
    facts = derive_trace_facts(item)
    assert facts["external_request_count"] is None
    observation = facts["tool_observations"][0]
    assert "query_timezone_missing_or_invalid" in observation["issues"]
    assert "query_interval_unavailable" in observation["issues"]
    assert observation["busy_intervals"][0]["issue"] == "busy_interval_unavailable_or_all_day"


def test_fact_context_is_optional_and_saved_even_when_judge_output_fails():
    item = saved_case()
    seen = []
    def complete(messages):
        data = json.loads(messages[1]["content"])
        seen.append(data)
        assert "expected" not in data
        return "invalid json"
    original = review(item, [], complete)
    enriched = review(item, [], complete, derive_facts=True)
    assert "computed_trace_facts" not in seen[0]
    assert seen[1]["computed_trace_facts"] == derive_trace_facts(item)
    assert "computed_trace_facts" not in original
    assert enriched["computed_trace_facts"] == derive_trace_facts(item)
    assert enriched["verdict"] == "UNCERTAIN"
