"""Opt-in offline preview of recorded Calendar facts; no agent integration."""
import argparse
import hashlib
import json
import os
from datetime import date
from pathlib import Path

from .saved_trace import validate_source
from .trace_facts import interval, interval_relationship

VERSION = 'calendar-renderer-preview-v1'
TEXT = {
    'en': {
        'free': 'Available (tool-reported; dedicated test calendar only).',
        'busy': 'Unavailable (tool-reported; dedicated test calendar only).',
        'unknown': 'Availability unknown; no free/busy conclusion is supported.',
        'scope': 'Scope: dedicated test calendar only.',
        'scope_unknown': 'Calendar scope cannot be verified from this record.',
        'query': 'Actual tool query', 'original': 'Original event timestamps',
        'converted': 'Event in requested zone', 'all_day': 'Original all-day dates (end exclusive)',
        'inside': 'This event contains the entire query interval.',
        'partial': 'This event overlaps the query but does not contain the entire query.',
        'empty': 'No conflicting events were returned.',
        'limited': 'All-day event: clock-time conversion and interval relationship are unavailable.',
        'union': 'Events are assessed individually; combined coverage was not calculated.',
    },
    'zh-TW': {
        'free': '可用（工具回報；僅專用測試行事曆）。',
        'busy': '不可用（工具回報；僅專用測試行事曆）。',
        'unknown': '可用性未知；目前紀錄不足以判定空閒或忙碌。',
        'scope': '範圍：僅專用測試行事曆。',
        'scope_unknown': '無法從此紀錄確認行事曆範圍。',
        'query': '工具實際查詢區間', 'original': '活動原始時間',
        'converted': '活動於指定時區', 'all_day': '原始全天日期（不含結束日）',
        'inside': '此活動包含整段查詢區間。',
        'partial': '此活動與查詢重疊，但未包含整段查詢區間。',
        'empty': '工具未回傳衝突活動。',
        'limited': '此為全天活動；無法轉換成起訖時刻或判定區間關係。',
        'union': '各活動分別判定；未計算多活動合併覆蓋範圍。',
    },
}


def _display(converted):
    local = converted['in_query_timezone']
    return f'{local["start"]["datetime"]} → {local["end"]["datetime"]} ({local["time_zone"]})'


def render_calendar_answer(run, *, language):
    """Render one completed single-tool run, independent of its LLM answer.

    This verifies recorded facts' internal consistency, not user intent, network
    authenticity, or Calendar completeness. Never silently fall back to LLM prose.
    """
    if language not in TEXT:
        raise ValueError('Explicit language must be en or zh-TW')
    text = TEXT[language]
    preview = {'version': VERSION, 'language': language, 'render_status': 'unsupported',
               'rendered_answer': None, 'evidence_refs': [], 'reasons': [], 'limitations': []}
    if not isinstance(run, dict) or run.get('status') != 'completed':
        preview['reasons'] = ['incomplete_or_missing_run']
        return preview
    events = run.get('events')
    if not isinstance(events, list) or any(not isinstance(e, dict) or not isinstance(e.get('type'), str) for e in events):
        preview['reasons'] = ['malformed_events']
        return preview
    tools = [(i, e) for i, e in enumerate(events) if e['type'] == 'tool']
    if len(tools) != 1 or tools[0][1].get('name') != 'check_availability':
        preview['reasons'] = ['requires_single_availability_tool_event']
        return preview
    index, event = tools[0]
    preview['evidence_refs'] = [{'event_index': index}]
    result = event.get('result')
    scope_known = isinstance(result, dict) and result.get('scope') == 'configured_test_calendar_only'
    def unknown(reason):
        preview.update(render_status='unknown', reasons=[reason], rendered_answer=(
            text['unknown'] + '\n' + text['scope' if scope_known else 'scope_unknown']))
        return preview
    if not isinstance(result, dict):
        return unknown('missing_tool_result')
    if 'error' in result:
        return unknown('tool_error')
    if not scope_known:
        return unknown('unverified_calendar_scope')
    if not isinstance(result.get('available'), bool) or not isinstance(result.get('busy_intervals'), list):
        return unknown('missing_availability_or_busy_array')
    try:
        args = event.get('arguments')
        args = json.loads(args) if isinstance(args, str) else args
        zone = result.get('time_zone') or (args.get('time_zone') if isinstance(args, dict) else None)
        if not isinstance(zone, str):
            return unknown('missing_query_timezone')
        query = interval(result['start'], result['end'], zone)
        query_text = _display(query)
    except (KeyError, TypeError, ValueError):
        return unknown('invalid_query_interval_or_timezone')
    busy = result['busy_intervals']
    if result['available'] != (not busy):
        return unknown('availability_conflicts_with_event_list')
    lines = [text['free' if result['available'] else 'busy'], f'{text["query"]}: {query_text}']
    for n, entry in enumerate(busy):
        try:
            start, end = entry['start'], entry['end']
            if 'date' in start or 'date' in end:
                if set(start) != {'date'} or set(end) != {'date'}:
                    return unknown('ambiguous_all_day_representation')
                if date.fromisoformat(end['date']) <= date.fromisoformat(start['date']):
                    return unknown('invalid_all_day_interval')
                lines.extend([f'{text["all_day"]}: {start["date"]} → {end["date"]}', text['limited']])
                preview['limitations'].append({'busy_index': n, 'issue': 'all_day_clock_times_unknown'})
            else:
                converted = interval(start['dateTime'], end['dateTime'], zone)
                relation = interval_relationship(query, converted)
                if not relation['overlaps_query']:
                    return unknown('returned_event_does_not_overlap_query')
                lines.extend([f'{text["original"]}: {start["dateTime"]} → {end["dateTime"]}',
                              f'{text["converted"]}: {_display(converted)}',
                              text['inside' if relation['query_fully_within_event'] else 'partial']])
        except (KeyError, TypeError, ValueError):
            return unknown('invalid_or_unsupported_event_interval')
    if not busy:
        lines.append(text['empty'])
    elif len(busy) > 1:
        lines.append(text['union'])
    preview.update(render_status='rendered', rendered_answer='\n'.join(lines))
    return preview


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True, help='New private preview file; never overwrite')
    parser.add_argument('--language', required=True, choices=TEXT)
    args = parser.parse_args(argv)
    source, output = Path(args.input), Path(args.output)
    if source.resolve() == output.resolve():
        parser.error('Preview must not overwrite the source')
    raw = source.read_bytes()
    try:
        items = validate_source(json.loads(raw))
    except (ValueError, TypeError) as error:
        parser.error(str(error))
    report = {'version': VERSION, 'source_sha256': hashlib.sha256(raw).hexdigest(),
              'mode': 'offline_preview_not_product_output', 'results': [
                  {'id': item['id'], 'original_answer': item.get('run', {}).get('answer') if isinstance(item.get('run'), dict) else None,
                   **render_calendar_answer(item.get('run'), language=args.language)} for item in items]}
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'x', encoding='utf-8', opener=lambda path, flags: os.open(path, flags, 0o600)) as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
