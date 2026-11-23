"""Retry/backoff helpers shared by all crawlers."""

import logging
import time
from typing import Callable, TypeVar

import httpx

logger = logging.getLogger(__name__)

T = TypeVar("T")

RETRY_STATUS = {429, 500, 502, 503, 504}


def get_with_retry(client: httpx.Client, url: str, attempts: int = 3, backoff: float = 1.5, **kwargs) -> httpx.Response:
    """GET with exponential backoff on network errors, 429 and 5xx responses.

    Returns the last response (even if it is still an error status) so callers keep
    their existing status-code handling; raises only if every attempt hit a network error.
    """
    last_exc: Exception = None
    resp = None
    for i in range(attempts):
        try:
            resp = client.get(url, **kwargs)
            if resp.status_code not in RETRY_STATUS:
                return resp
            wait = backoff * (2 ** i)
            retry_after = resp.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                wait = max(wait, min(int(retry_after), 30))
            logger.warning("GET %s -> %s, retry %d/%d in %.1fs", url, resp.status_code, i + 1, attempts, wait)
        except httpx.TransportError as e:
            last_exc = e
            wait = backoff * (2 ** i)
            logger.warning("GET %s failed (%s), retry %d/%d in %.1fs", url, type(e).__name__, i + 1, attempts, wait)
        if i < attempts - 1:
            time.sleep(wait)
    if resp is not None:
        return resp
    raise last_exc


def call_with_retry(fn: Callable[[], T], attempts: int = 3, backoff: float = 1.5, label: str = "call") -> T:
    """Retries an arbitrary callable (e.g. google-play-scraper) on any exception."""
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:
            if i == attempts - 1:
                raise
            wait = backoff * (2 ** i)
            logger.warning("%s failed (%s), retry %d/%d in %.1fs", label, type(e).__name__, i + 1, attempts, wait)
            time.sleep(wait)
