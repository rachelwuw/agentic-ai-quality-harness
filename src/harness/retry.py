"""Bounded retries for transient read/inference transport failures only."""
import time
from urllib.error import HTTPError, URLError
try:
    from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout as RequestsTimeout
except ImportError:
    REQUEST_ERRORS = ()
else:
    REQUEST_ERRORS = (RequestsConnectionError, RequestsTimeout)

TRANSIENT_STATUS = {429, 500, 502, 503, 504}


def transient(error):
    if isinstance(error, HTTPError):
        return error.code in TRANSIENT_STATUS
    return isinstance(error, (URLError, TimeoutError, ConnectionError) + REQUEST_ERRORS)


def retry_call(operation, attempts, *, retryable=transient, retries=2):
    for index in range(retries + 1):
        try:
            result = operation()
        except Exception as error:
            will_retry = index < retries and retryable(error)
            delay = 2 ** index if will_retry else 0
            attempts.append({"attempt": index + 1, "outcome": "error",
                             "error_type": type(error).__name__,
                             "retry": will_retry, "wait_seconds": delay})
            if not will_retry:
                raise
            time.sleep(delay)
        else:
            attempts.append({"attempt": index + 1, "outcome": "success"})
            return result
