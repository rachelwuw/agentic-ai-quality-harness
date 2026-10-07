"""Authorize Google Calendar and check the configured test calendar (read only)."""
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

CONFIG_DIR = Path.home() / '.config' / 'agentic-ai-quality-harness'
SCOPES = ['https://www.googleapis.com/auth/calendar.events.owned.readonly']


def save_token(path, contents):
    """Publish a complete token file with owner-only permissions."""
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(contents)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    from google.auth.transport.requests import AuthorizedSession, Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    settings = json.loads((CONFIG_DIR / 'calendar.json').read_text())
    calendar_id = settings['calendar_id']
    if not calendar_id or calendar_id == 'primary':
        raise ValueError('Configure the dedicated test calendar, not primary.')
    token = CONFIG_DIR / 'google-readonly-token.json'
    credentials = None
    if token.exists():
        credentials = Credentials.from_authorized_user_file(str(token))
        if not credentials.has_scopes(SCOPES):
            raise ValueError('Saved credentials do not have the required read-only scope.')
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    if not credentials or not credentials.valid:
        print('Google authorization: read events on calendars you own.', flush=True)
        print('This check only queries your configured test calendar. No events will be created.', flush=True)
        flow = InstalledAppFlow.from_client_secrets_file(str(CONFIG_DIR / 'google-client.json'), SCOPES)
        credentials = flow.run_local_server(
            host='127.0.0.1', port=0, timeout_seconds=600,
            success_message='Authorization completed. Return to VS Code Terminal.',
        )
    save_token(token, credentials.to_json())
    now = datetime.now(timezone.utc)
    with AuthorizedSession(credentials) as session:
        response = session.get(
            'https://www.googleapis.com/calendar/v3/calendars/' + quote(calendar_id, safe='') + '/events',
            params={'timeMin': now.isoformat(), 'timeMax': (now + timedelta(days=7)).isoformat(),
                    'maxResults': 10, 'singleEvents': 'true', 'fields': 'items(id),nextPageToken'},
            timeout=30,
        )
        if response.status_code != 200:
            raise RuntimeError(f'Calendar read failed (HTTP {response.status_code}). Check access and calendar ID.')
        result = response.json()
    print('PASS: Connected to the dedicated test calendar.')
    count = len(result.get('items', []))
    print(f'Upcoming events in the next 7 days: {count}' + (' or more' if result.get('nextPageToken') else ''))
    print('Read-only check complete. No events were created or modified.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        # OAuth errors may contain sensitive responses; never dump their text.
        print(f'Setup failed ({type(error).__name__}). Check configuration, consent, or connectivity.', file=sys.stderr)
        sys.exit(1)
