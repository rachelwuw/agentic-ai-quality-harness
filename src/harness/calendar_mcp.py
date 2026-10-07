"""Small stdio MCP adapter; shares the existing read-only Calendar tool."""
from datetime import datetime
from zoneinfo import ZoneInfo
from mcp.server.fastmcp import FastMCP
from .calendar_tools import connect, resolve_local_interval, LocalTimeError

server = FastMCP('Rachel Calendar Read Only', instructions=(
    'Only the configured test calendar is checked. No booking or event changes are supported. '
    'Ask for missing date/time/duration. Pass local times without offsets and an IANA time zone; Python resolves daylight saving. '
    'Never report availability without a successful tool result. Errors mean unknown availability.'
))


@server.tool()
def check_availability(start: str, end: str, time_zone: str = 'America/Los_Angeles') -> dict:
    """Check real busy intervals on the dedicated test calendar only.

    start/end must be local YYYY-MM-DDTHH:MM:SS without offsets.
    time_zone is an IANA name; Python computes the correct UTC offset.
    Ambiguous or nonexistent daylight-saving times require clarification.
    Cross-midnight intervals are supported. Correct invalid formatting and retry the original interval; DST ambiguity requires user clarification.
    Does not reserve or create an event. Other calendars are not checked.
    """
    try:
        start, end = resolve_local_interval(start, end, time_zone)
    except LocalTimeError as error:
        return error.result()
    calendar = connect()
    try:
        return {**calendar.check_availability(start, end), 'time_zone': time_zone}
    finally:
        calendar.session.close()


@server.tool()
def get_current_time() -> dict:
    """Get current local time for interpreting 'today'/'tomorrow'; default timezone Los Angeles."""
    return {'now': datetime.now(ZoneInfo('America/Los_Angeles')).isoformat(),
            'timezone': 'America/Los_Angeles'}


if __name__ == '__main__':
    server.run(transport='stdio')
