"""Real, read-only availability checks on the configured test calendar."""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from urllib.parse import quote
from .calendar_setup import CONFIG_DIR, SCOPES, save_token


class CalendarError(RuntimeError):
    """Safe error message that does not include credentials or API bodies."""


class LocalTimeError(ValueError):
    """Structured, credential-free validation feedback for model-facing tools."""
    def __init__(self, code, message, action):
        super().__init__(message)
        self.code, self.action = code, action

    def result(self):
        return {'error': self.code, 'available': None, 'message': str(self),
                'action': self.action, 'cross_midnight_supported': True}


def validate_interval(start, end):
    values = []
    for value in (start, end):
        if not isinstance(value, str) or not re.fullmatch(
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})', value
        ):
            raise ValueError('Use timestamps with seconds and an explicit timezone offset.')
        values.append(datetime.fromisoformat(value.replace('Z', '+00:00')))
    if not values[0] < values[1]:
        raise ValueError('End must be later than start.')
    if values[1] - values[0] > timedelta(days=31):
        raise ValueError('Check at most 31 days at a time.')
    return tuple(value.isoformat() for value in values)


def resolve_local_interval(start, end, time_zone):
    """Resolve wall-clock times in Python; reject DST gaps and ambiguous folds."""
    try:
        zone = ZoneInfo(time_zone)
    except (ZoneInfoNotFoundError, TypeError, ValueError):
        raise LocalTimeError('invalid_time_zone', 'Use an IANA time zone, such as America/Los_Angeles.', 'Ask for the intended region if unknown; do not guess.') from None
    resolved = []
    for value in (start, end):
        if not isinstance(value, str) or not re.fullmatch(
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value
        ):
            raise LocalTimeError('invalid_time_format', 'Expected YYYY-MM-DDTHH:MM:SS without offset, e.g. 2026-10-07T00:15:00.', 'Correct your timestamp formatting and retry using the original user dates and times. Cross-midnight intervals are supported; do not change the requested interval or invent a limitation.')
        try:
            local = datetime.fromisoformat(value)
        except ValueError:
            raise LocalTimeError('invalid_local_date', 'Invalid calendar date or clock time.', 'Ask for a valid date/time; do not silently change the user request.') from None
        candidates = {}
        for fold in (0, 1):
            aware = local.replace(tzinfo=zone, fold=fold)
            instant = aware.astimezone(timezone.utc)
            if instant.astimezone(zone).replace(tzinfo=None) == local:
                candidates[instant] = aware
        if len(candidates) != 1:
            raise LocalTimeError('dst_time_requires_clarification', 'Local time is nonexistent or ambiguous due to daylight saving.', 'Ask the user for an unambiguous valid local time; do not retry by guessing.')
        resolved.append(next(iter(candidates.values())).isoformat())
    # Compare absolute instants, including intervals crossing DST changes.
    try:
        return validate_interval(*resolved)
    except ValueError as error:
        raise LocalTimeError('invalid_time_interval', str(error), 'Ask for a valid interval; end must be later than start and duration at most 31 days.') from None


def check_local_availability(calendar, start, end, time_zone):
    start, end = resolve_local_interval(start, end, time_zone)
    return {**calendar.check_availability(start, end), 'time_zone': time_zone}


class CalendarTools:
    def __init__(self, calendar_id, session):
        if not isinstance(calendar_id, str) or not calendar_id.strip() or calendar_id == 'primary':
            raise ValueError('Configure a dedicated test calendar, not primary.')
        self.calendar_id = calendar_id
        self.session = session

    def check_availability(self, start, end):
        """Check [start, end); a failed/partial read never reports availability."""
        start, end = validate_interval(start, end)
        url = 'https://www.googleapis.com/calendar/v3/calendars/' + quote(self.calendar_id, safe='') + '/events'
        params = {'timeMin': start, 'timeMax': end, 'singleEvents': 'true',
                  'showDeleted': 'false', 'orderBy': 'startTime', 'maxResults': 250,
                  'fields': 'nextPageToken,items(status,transparency,start,end)'}
        busy = []
        seen_pages = set()
        for _ in range(100):
            try:
                response = self.session.get(url, params=dict(params), timeout=30)
                if response.status_code != 200:
                    raise CalendarError(f'Calendar read failed (HTTP {response.status_code}).')
                data = response.json()
                items = data.get('items', [])
                if not isinstance(items, list):
                    raise ValueError('Invalid event list')
                for event in items:
                    if event.get('status') == 'cancelled' or event.get('transparency') == 'transparent':
                        continue
                    if not event.get('start') or not event.get('end'):
                        raise ValueError('Missing event interval')
                    # Google filters overlaps, including all-day and recurring instances.
                    busy.append({'start': event['start'], 'end': event['end']})
                page = data.get('nextPageToken')
            except CalendarError:
                raise
            except Exception:
                raise CalendarError('Calendar query failed; availability is unknown.') from None
            if not page:
                return {'start': start, 'end': end, 'available': not busy,
                        'busy_intervals': busy, 'source': 'google_calendar',
                        'scope': 'configured_test_calendar_only'}
            if not isinstance(page, str) or page in seen_pages:
                raise CalendarError('Incomplete Calendar response; availability is unknown.')
            seen_pages.add(page)
            params['pageToken'] = page
        raise CalendarError('Calendar pagination limit reached; availability is unknown.')


def connect():
    from google.auth.transport.requests import AuthorizedSession, Request
    from google.oauth2.credentials import Credentials
    settings = json.loads((CONFIG_DIR / 'calendar.json').read_text())
    token = CONFIG_DIR / 'google-readonly-token.json'
    if not token.exists():
        raise CalendarError('Run python -m harness.calendar_setup to authorize first.')
    credentials = Credentials.from_authorized_user_file(str(token))
    if not credentials.has_scopes(SCOPES):
        raise CalendarError('Required read-only permission is missing.')
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        save_token(token, credentials.to_json())
    if not credentials.valid:
        raise CalendarError('Authorization expired. Run the Calendar setup again.')
    return CalendarTools(settings['calendar_id'], AuthorizedSession(credentials))


def main():
    parser = argparse.ArgumentParser(description='Read-only check of the test calendar; no event writes.')
    parser.add_argument('--start', required=True)
    parser.add_argument('--end', required=True)
    args = parser.parse_args()
    try:
        validate_interval(args.start, args.end)  # Reject invalid input before connecting.
        tools = connect()
        try:
            result = tools.check_availability(args.start, args.end)
        finally:
            tools.session.close()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print('No events were created or modified.')
        return 0
    except (CalendarError, ValueError) as error:
        print(str(error), file=sys.stderr)
    except Exception:
        print('Calendar connection failed; availability is unknown. Check setup and connectivity.', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
