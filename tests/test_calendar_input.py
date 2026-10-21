"""Regression for missing-date model inference; no live model or Calendar calls."""
import json
from datetime import datetime
from pathlib import Path

import pytest

from harness import calendar_agent as agent
from harness.calendar_input import date_clarification

MISSING = 'Is 09:10–09:20 America/Los_Angeles free on the dedicated test calendar?'
NOW = datetime.fromisoformat('2029-01-01T12:00:00-08:00')


@pytest.mark.parametrize('language', ['en', 'zh-TW'])
@pytest.mark.parametrize('prompt', [MISSING, '請查詢台北 09:10 到 09:20 有空嗎？',
    'Am I free tomorrow at 09:10?', 'October 6 at 10 AM?', '01/02/2029 09:10–09:20',
    '2029-02-30 09:10–09:20', '2029年2月30日 09:10–09:20'])
def test_no_recognized_valid_date_prevents_inference_and_calendar(prompt, language):
    def must_not_run(*_): pytest.fail('Do not invoke a date-guessing model')
    class Calendar:
        def check_availability(self, *_): pytest.fail('Do not query Calendar')
    run = agent.run_calendar_agent(prompt, must_not_run, Calendar(), now=NOW, renderer_language=language)
    assert run['status'] == 'completed' and run['answer'] == '' and run['events'] == []
    assert run['input_validation']['origin'] == 'deterministic_input_validation'
    assert run['input_validation']['model_called'] is False
    assert 'YYYY-MM-DD' in run['input_validation']['message']
    assert run['product_output']['render_status'] == 'unsupported'
    assert run['product_output']['rendered_answer'] is None
    assert run['product_output']['provenance']['user_intent_verified'] is False


@pytest.mark.parametrize('prompt', [
    '2029-01-23 09:10–09:20', '2029年1月23日 09:10–09:20',
    'January 23, 2029 at 09:10', 'JANUARY 23rd 2029 at 09:10',
    '23 January 2029 at 09:10', '23rd January 2029 at 09:10',
    '2028-02-29 09:10–09:20', 'Check 2029-07-25 07:10 Asia/Taipei',
    '2029-01-23T09:10:00 to 09:20',
])
def test_supported_full_date_formats_are_recognized(prompt):
    assert date_clarification(prompt, 'en') is None


def test_dated_prompt_still_requires_model_and_tool_grading():
    calls = []
    result = agent.run_calendar_agent('2029-01-23 09:10–09:20 America/Los_Angeles',
        lambda *_: calls.append(1) or {'role': 'assistant', 'content': 'No tool, untrusted prose.'},
        None, now=NOW, renderer_language='en')
    assert calls == [1] and result['answer'] == 'No tool, untrusted prose.'
    assert 'input_validation' not in result
    assert result['product_output']['render_status'] == 'unsupported'


def test_non_renderer_legacy_path_keeps_original_behavior():
    seen = []
    result = agent.run_calendar_agent(MISSING,
        lambda *_: seen.append(1) or {'role': 'assistant', 'content': 'Which date?'}, None, now=NOW)
    assert seen == [1] and result['answer'] == 'Which date?'
    assert 'input_validation' not in result and 'product_output' not in result


@pytest.mark.parametrize('language', ['en', 'zh-TW'])
def test_cli_missing_date_needs_no_runtime_oauth_and_writes_honest_trace(monkeypatch, tmp_path, capsys, language):
    import sys
    def blocked(*_, **__): pytest.fail('No runtime lookup, model or OAuth connection')
    monkeypatch.setattr(agent, 'LocalClient', blocked)
    monkeypatch.setattr(agent, 'connect', blocked)
    out = tmp_path / 'new.json'
    monkeypatch.setattr(sys, 'argv', ['calendar_agent', MISSING, '--renderer', 'python',
                                     '--language', language, '--output', str(out)])
    assert agent.main() == 1
    r = json.loads(out.read_text())
    assert r['model'] is None and r['base_url'] is None and r['answer'] == ''
    assert r['events'] == [] and r['input_validation']['model_called'] is False
    assert r['input_validation']['message'] in capsys.readouterr().out
    assert out.stat().st_mode & 0o777 == 0o600
