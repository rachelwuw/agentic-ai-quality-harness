"""Conservative explicit-date gate for the opt-in v1 renderer path.

This recognizes date evidence, not user intent or correspondence to tool dates.
Relative/ambiguous/unrecognized formats require clarification instead of guessing.
"""
import re
from datetime import date

MONTHS = {name.lower(): n for n, name in enumerate((
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'), 1)}
MONTH = '|'.join(MONTHS)
PATTERNS = (
    re.compile(r'(?<!\w)(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})(?![0-9])'),
    re.compile(r'(?<![0-9])(?P<year>[0-9]{4})\s*年\s*(?P<month>[0-9]{1,2})\s*月\s*(?P<day>[0-9]{1,2})\s*日'),
    re.compile(rf'\b(?P<month>{MONTH})\s+(?P<day>[0-9]{{1,2}})(?:st|nd|rd|th)?(?:,\s*|\s+)(?P<year>[0-9]{{4}})\b', re.I),
    re.compile(rf'\b(?P<day>[0-9]{{1,2}})(?:st|nd|rd|th)?\s+(?P<month>{MONTH})\s+(?P<year>[0-9]{{4}})\b', re.I),
)


def date_clarification(prompt, language):
    """None when a full valid date is recognizable; otherwise an explicit request.

    Month-name formats require the year. No current date, environment clock,
    inferred year, or model-proposed timestamp is accepted as user date evidence.
    """
    if not isinstance(prompt, str):
        raise ValueError('Calendar prompt must be text')
    for pattern in PATTERNS:
        for match in pattern.finditer(prompt):
            fields = match.groupdict()
            month = MONTHS.get(fields['month'].lower(), fields['month'])
            try:
                date(int(fields['year']), int(month), int(fields['day']))
            except ValueError:
                continue
            return None
    return {'status': 'needs_explicit_date', 'origin': 'deterministic_input_validation',
            'model_called': False,
            'message': ('請提供完整日期（例如 YYYY-MM-DD），再查詢行事曆；目前尚未查詢。'
                        if language == 'zh-TW' else
                        'Please provide a full date (for example YYYY-MM-DD) before checking availability; no calendar query has been made.')}
