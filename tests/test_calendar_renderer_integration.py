import copy
import json
import sys
from datetime import datetime

import pytest

from harness import calendar_agent as agent
from harness.calendar_evaluate import ControlledCalendar
from harness.calendar_tools import CalendarError

NOW = datetime.fromisoformat('2027-07-13T12:00:00-07:00')
ARGS = {'start':'2027-07-14T11:15:00','end':'2027-07-14T11:45:00','time_zone':'America/Los_Angeles'}
RAW = 'Unverified original model prose; renderer must not use this as fallback.'


def call(args=ARGS):
    return {'role':'assistant','tool_calls':[{'id':'one','type':'function',
        'function':{'name':'check_availability','arguments':json.dumps(args)}}]}


class Model:
    def __init__(self, replies=None):
        self.replies = iter(replies or [call(), {'role':'assistant','content':RAW}])
        self.seen = []
    def __call__(self, messages, tools):
        self.seen.append(copy.deepcopy((messages,tools)))
        return next(self.replies)


def calendar(fixture='busy_fixture'):
    return ControlledCalendar(fixture, {'start':'2027-07-14T11:00:00-07:00','end':'2027-07-14T11:30:00-07:00'})


@pytest.mark.parametrize('language,fixture,prefix', [
    ('en','busy_fixture','Unavailable ('),('en','empty_fixture','Available ('),
    ('zh-TW','busy_fixture','不可用（'),('zh-TW','empty_fixture','可用（')])
def test_actual_scripted_run_adds_product_only_without_extra_calls(language, fixture, prefix, monkeypatch):
    import socket
    monkeypatch.setattr(socket,'socket',lambda *a,**k:pytest.fail('No network allowed'))
    plain_model, rendered_model = Model(), Model()
    plain_cal, rendered_cal = calendar(fixture), calendar(fixture)
    legacy = agent.run_calendar_agent('Check 2027-07-14 11:15–11:45 America/Los_Angeles',plain_model,plain_cal,now=NOW)
    rendered = agent.run_calendar_agent('Check 2027-07-14 11:15–11:45 America/Los_Angeles',rendered_model,rendered_cal,now=NOW,renderer_language=language)
    assert rendered_model.seen == plain_model.seen and len(rendered_model.seen)==2
    assert rendered_cal.calls == plain_cal.calls and len(rendered_cal.calls)==1
    assert 'product_output' not in legacy
    product = rendered.pop('product_output')
    assert rendered == legacy and rendered['answer']==RAW
    assert product['render_status']=='rendered' and product['rendered_answer'].startswith(prefix)
    assert product['version']=='calendar-renderer-preview-v1'
    assert product['provenance']['source']=='current_python_agent_run'
    assert product['provenance']['user_intent_verified'] is False


def test_tool_error_unknown_and_no_tool_is_not_assumed_clarification():
    class Broken:
        def check_availability(self,*args):raise CalendarError('private')
    error = agent.run_calendar_agent('Check 2027-07-14 11:15–11:45 America/Los_Angeles',Model(),Broken(),now=NOW,renderer_language='en')
    assert error['product_output']['render_status']=='unknown'
    assert error['product_output']['rendered_answer'].startswith('Availability unknown;')
    no_tool = agent.run_calendar_agent('Check 2027-07-14 11:15–11:45 America/Los_Angeles',Model([{'role':'assistant','content':'Free!'}]),calendar(),now=NOW,renderer_language='en')
    assert no_tool['product_output']['render_status']=='unsupported'
    assert no_tool['product_output']['rendered_answer'] is None
    assert no_tool['answer']=='Free!'


def test_retry_multiple_calls_and_model_error_remain_unsupported():
    for replies in [
        [call({**ARGS,'start':'bad'}),call(),{'role':'assistant','content':RAW}],
        [call(),call(),{'role':'assistant','content':RAW}],
    ]:
        result = agent.run_calendar_agent('Check 2027-07-14 11:15–11:45 America/Los_Angeles',Model(replies),calendar(),now=NOW,renderer_language='en')
        assert result['product_output']['render_status']=='unsupported'
        assert result['product_output']['rendered_answer'] is None
    class Failed:
        attempt_events=[]
        def __call__(self,*a):raise ValueError('model failure')
    result = agent.run_calendar_agent('Check 2027-07-14 11:15–11:45 America/Los_Angeles',Failed(),calendar(),now=NOW,renderer_language='en')
    assert result['status']=='model_error'
    assert result['product_output']['render_status']=='unsupported'


@pytest.mark.parametrize('flags', [['--renderer','python'],['--language','en'],['--renderer','python','--language','es']])
def test_invalid_cli_opt_in_rejected_before_runtime_or_google(flags,monkeypatch):
    monkeypatch.setattr(sys,'argv',['calendar_agent','Check 2027-07-14 11:15–11:45 America/Los_Angeles',*flags])
    monkeypatch.setattr(agent,'LocalClient',lambda:pytest.fail('Must validate flags before runtime'))
    with pytest.raises(SystemExit):agent.main()


def test_existing_trace_rejected_before_calls_and_invalid_api_language_rejected(tmp_path,monkeypatch):
    output=tmp_path/'old.json';output.write_text('preserved')
    monkeypatch.setattr(sys,'argv',['calendar_agent','Check','--renderer','python','--language','en','--output',str(output)])
    monkeypatch.setattr(agent,'LocalClient',lambda:pytest.fail('Existing output must stop before runtime'))
    with pytest.raises(SystemExit):agent.main()
    assert output.read_text()=='preserved'
    model=Model();c=calendar()
    with pytest.raises(ValueError):agent.run_calendar_agent('Check',model,c,renderer_language='es')
    assert not model.seen and not c.calls


@pytest.mark.parametrize('mode', ['default','rendered','unsupported','unknown'])
def test_cli_routes_output_and_preserves_raw_trace(mode,tmp_path,monkeypatch,capsys):
    class Client(Model):
        model='scripted';base='no-network'
        def models(self):return {'data':[]}
    client = Client([{'role':'assistant','content':RAW}]) if mode=='unsupported' else Client()
    c = calendar()
    class Session:
        closed=False
        def close(self):self.closed=True
    c.session=Session()
    if mode=='unknown':
        def fail(*args):raise CalendarError('private')
        c.check_availability=fail
    output=tmp_path/'run.json'
    flags=[] if mode=='default' else ['--renderer','python','--language','en']
    monkeypatch.setattr(sys,'argv',['calendar_agent','Check 2027-07-14 11:15–11:45 America/Los_Angeles','--output',str(output),*flags])
    monkeypatch.setattr(agent,'LocalClient',lambda:client)
    monkeypatch.setattr(agent,'connect',lambda:c)
    assert agent.main()==(1 if mode in ('unknown','unsupported') else 0)
    saved=json.loads(output.read_text());stdout=capsys.readouterr().out
    assert saved['answer']==RAW and c.session.closed
    if mode=='default':
        assert 'product_output' not in saved and '\nAssistant: '+RAW in stdout
    else:
        assert '\nAssistant:' not in stdout and RAW not in stdout
        assert output.stat().st_mode & 0o777 == 0o600
        assert saved['product_output']['render_status']==mode
        assert saved['product_output']['reasons'] if mode in ('unknown','unsupported') else not saved['product_output']['reasons']
