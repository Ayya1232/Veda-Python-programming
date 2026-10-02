"""Task 25 - Retry and Timeout System for API Calls.

A reusable API client built on `requests` with:
  * request timeouts (connect + read)
  * limited retries for transient failures only
  * exponential backoff with jitter (and Retry-After support)
  * logging and clear failure handling
"""

import logging
import random
import time

import requests

logger = logging.getLogger("api_client")


# ---------- Custom exceptions (clear failure handling) ----------
class APIClientError(Exception):
    """Base class for all errors raised by this client."""


class NonRetryableError(APIClientError):
    """Permanent failure (e.g. 400/401/404). Retrying will not help."""

    def __init__(self, status_code, message):
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code


class RetryExhaustedError(APIClientError):
    """All retry attempts were used and the request still failed."""

    def __init__(self, attempts, last_error):
        super().__init__(f"Failed after {attempts} attempts. Last error: {last_error}")
        self.attempts = attempts
        self.last_error = last_error


# ---------- The client ----------
class APIClient:
    # Transient HTTP statuses worth retrying. Other 4xx errors are NOT retried.
    RETRY_STATUS_CODES = {408, 429, 500, 502, 503, 504}

    def __init__(
        self,
        base_url="",
        timeout=(3.05, 10),   # (connect timeout, read timeout) in seconds
        max_retries=3,        # retries AFTER the first attempt
        backoff_factor=0.5,   # delay = backoff_factor * 2**attempt
        max_backoff=30.0,     # cap so delays never grow forever
        jitter=True,          # randomise delay to avoid thundering herd
        headers=None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        self.jitter = jitter
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    # -- backoff -----------------------------------------------------
    def _backoff_delay(self, attempt, response=None):
        """Exponential backoff: 0.5s, 1s, 2s, 4s ... capped at max_backoff."""
        delay = min(self.backoff_factor * (2 ** attempt), self.max_backoff)

        # Respect the server's Retry-After header if it sent one (e.g. on 429).
        if response is not None:
            retry_after = response.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                delay = max(delay, min(float(retry_after), self.max_backoff))

        if self.jitter:
            delay *= random.uniform(0.5, 1.0)
        return delay

    # -- core request ------------------------------------------------
    def request(self, method, path, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}" if self.base_url else path
        kwargs.setdefault("timeout", self.timeout)
        total_attempts = self.max_retries + 1
        last_error = None

        for attempt in range(total_attempts):
            response = None
            try:
                logger.info("Attempt %d/%d: %s %s", attempt + 1, total_attempts, method, url)
                response = self.session.request(method, url, **kwargs)

                if response.status_code < 400:
                    logger.info("Success: HTTP %d", response.status_code)
                    return response

                if response.status_code not in self.RETRY_STATUS_CODES:
                    # Client error like 400/401/403/404 -> fail fast, no retry.
                    raise NonRetryableError(response.status_code, response.reason)

                last_error = f"HTTP {response.status_code}"
                logger.warning("Retryable status: %s", last_error)

            except NonRetryableError:
                logger.error("Non-retryable error, giving up.")
                raise
            except (requests.Timeout, requests.ConnectionError) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                logger.warning("Network problem: %s", last_error)
            except requests.RequestException as exc:
                # Invalid URL, bad params, etc. - retrying won't fix it.
                logger.error("Unrecoverable request error: %s", exc)
                raise APIClientError(str(exc)) from exc

            if attempt < self.max_retries:
                delay = self._backoff_delay(attempt, response)
                logger.info("Retrying in %.2fs...", delay)
                time.sleep(delay)

        logger.error("Giving up after %d attempts.", total_attempts)
        raise RetryExhaustedError(total_attempts, last_error)

    # -- convenience helpers -----------------------------------------
    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)


# ---------- Demo: a local flaky server so no internet is needed ----------
if __name__ == "__main__":
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s")
    hits = {"count": 0}

    class FlakyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/flaky":
                hits["count"] += 1
                code = 503 if hits["count"] < 3 else 200   # fails twice, then works
            elif self.path == "/missing":
                code = 404
            else:
                code = 500                                  # always fails
            self.send_response(code)
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}' if code == 200 else b"error")

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 8765), FlakyHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    client = APIClient("http://127.0.0.1:8765", max_retries=3, backoff_factor=0.2)

    print("\n--- 1. Flaky endpoint (recovers after retries) ---")
    print("Result:", client.get("/flaky").json())

    print("\n--- 2. 404 (not retried) ---")
    try:
        client.get("/missing")
    except NonRetryableError as e:
        print("Caught:", e)

    print("\n--- 3. Always failing (retries exhausted) ---")
    try:
        client.get("/always-down")
    except RetryExhaustedError as e:
        print("Caught:", e)

    server.shutdown()