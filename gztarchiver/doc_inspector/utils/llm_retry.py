import sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests
from tenacity import Retrying, retry_if_exception, stop_after_attempt, wait_exponential_jitter

DEFAULT_REQUESTS_PER_MINUTE = 20
DEFAULT_MAX_RETRIES = 5
REQUEST_TIMEOUT_SECONDS = 30
RETRY_AFTER_CAP_SECONDS = 300

_exponential_jitter = wait_exponential_jitter(initial=1, max=60, jitter=1)


def resolve_requests_per_minute(value):
    if value is None:
        return float(DEFAULT_REQUESTS_PER_MINUTE)
    try:
        rpm = float(value)
    except (TypeError, ValueError):
        return float(DEFAULT_REQUESTS_PER_MINUTE)
    return max(0.0, rpm)


def resolve_max_retries(value):
    if value is None:
        return DEFAULT_MAX_RETRIES
    try:
        retries = int(value)
    except (TypeError, ValueError):
        return DEFAULT_MAX_RETRIES
    return max(0, retries)


def rate_limit_delay_seconds(requests_per_minute):
    rpm = resolve_requests_per_minute(requests_per_minute)
    return 60.0 / rpm if rpm else 0.0


def post_with_retry(url, headers, payload, max_retries=DEFAULT_MAX_RETRIES):
    retryer = Retrying(
        retry=retry_if_exception(_is_retryable),
        stop=stop_after_attempt(resolve_max_retries(max_retries) + 1),
        wait=_wait_strategy,
        before_sleep=_log_retry,
        reraise=True,
    )

    def _post():
        response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response

    return retryer(_post)


def _is_retryable(exc):
    if isinstance(exc, (requests.ConnectionError, requests.Timeout)):
        return True
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        status = exc.response.status_code
        return status == 429 or 500 <= status < 600
    return False


def _wait_strategy(retry_state):
    retry_after = _retry_after_seconds(retry_state.outcome.exception())
    if retry_after is not None:
        return min(retry_after, RETRY_AFTER_CAP_SECONDS)
    return _exponential_jitter(retry_state)


def _retry_after_seconds(exc):
    response = getattr(exc, "response", None)
    if response is None:
        return None
    value = response.headers.get("Retry-After")
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        retry_at = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=timezone.utc)
    return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())


def _log_retry(retry_state):
    exc = retry_state.outcome.exception()
    print(f"LLM request failed ({exc}); retry attempt {retry_state.attempt_number}", file=sys.stderr)
