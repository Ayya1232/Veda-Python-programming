#!/usr/bin/env python3
"""Concurrent URL Checker

Checks the availability and response time of many URLs at once using
requests + ThreadPoolExecutor.

Usage:
    python url_checker.py                       # checks the built-in sample URLs
    python url_checker.py https://a.com https://b.com
    python url_checker.py -f urls.txt -w 8 -t 5
"""

import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional

import requests

DEFAULT_URLS = [
    "https://www.python.org",
    "https://github.com",
    "https://pypi.org",
    "https://httpbin.org/status/404",
    "https://httpbin.org/delay/10",          # will time out with a short timeout
    "https://this-domain-does-not-exist-12345.com",
    "not-a-valid-url",
]

DEFAULT_TIMEOUT = 5      # seconds; never make requests without one
DEFAULT_WORKERS = 10     # bounded pool; no need for one thread per URL


@dataclass
class Result:
    url: str
    status_code: Optional[int] = None
    elapsed: Optional[float] = None   # seconds
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.status_code is not None and 200 <= self.status_code < 400


def check_url(url: str, timeout: float, session: requests.Session) -> Result:
    """Check a single URL. Never raises: failures are captured in the Result."""
    start = time.perf_counter()
    try:
        # GET with stream=True so we don't download the whole body;
        # elapsed time then measures time to response headers.
        with session.get(url, timeout=timeout, stream=True, allow_redirects=True) as resp:
            elapsed = time.perf_counter() - start
            return Result(url, status_code=resp.status_code, elapsed=elapsed)
    except requests.exceptions.Timeout:
        return Result(url, error=f"Timeout after {timeout}s")
    except requests.exceptions.SSLError:
        return Result(url, error="SSL error")
    except requests.exceptions.ConnectionError:
        return Result(url, error="Connection failed (DNS/refused/reset)")
    except (requests.exceptions.MissingSchema,
            requests.exceptions.InvalidSchema,
            requests.exceptions.InvalidURL):
        return Result(url, error="Invalid URL")
    except requests.exceptions.RequestException as exc:
        return Result(url, error=f"Request error: {type(exc).__name__}")


def check_all(urls, workers=DEFAULT_WORKERS, timeout=DEFAULT_TIMEOUT):
    """Check URLs concurrently. Returns results in the same order as `urls`."""
    workers = max(1, min(workers, len(urls)))
    results = {}
    # requests.Session is used read-only for connection pooling; sharing it
    # across threads for simple GETs is widely done, but each thread gets
    # its own adapter pool slot, so this is fine here.
    with requests.Session() as session, ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(check_url, u, timeout, session): u for u in urls}
        for fut in as_completed(futures):
            results[futures[fut]] = fut.result()
    return [results[u] for u in urls]


def print_status_report(results):
    print("\n=== STATUS-CODE REPORT ===")
    print(f"{'URL':<50} {'STATUS':<8} RESULT")
    print("-" * 80)
    for r in results:
        if r.status_code is not None:
            label = "UP" if r.ok else "HTTP ERROR"
            print(f"{r.url[:49]:<50} {r.status_code:<8} {label}")
        else:
            print(f"{r.url[:49]:<50} {'-':<8} DOWN ({r.error})")
    up = sum(r.ok for r in results)
    print("-" * 80)
    print(f"Summary: {up}/{len(results)} healthy, {len(results) - up} failing")


def print_time_report(results):
    print("\n=== RESPONSE-TIME REPORT ===")
    timed = sorted((r for r in results if r.elapsed is not None), key=lambda r: r.elapsed)
    if not timed:
        print("No successful responses to time.")
        return
    for r in timed:
        print(f"{r.url[:49]:<50} {r.elapsed * 1000:8.0f} ms")
    times = [r.elapsed * 1000 for r in timed]
    print("-" * 80)
    print(f"Fastest: {min(times):.0f} ms | Slowest: {max(times):.0f} ms | "
          f"Average: {statistics.mean(times):.0f} ms")


def main():
    parser = argparse.ArgumentParser(description="Concurrent URL checker")
    parser.add_argument("urls", nargs="*", help="URLs to check")
    parser.add_argument("-f", "--file", help="text file with one URL per line")
    parser.add_argument("-w", "--workers", type=int, default=DEFAULT_WORKERS,
                        help=f"max threads (default {DEFAULT_WORKERS})")
    parser.add_argument("-t", "--timeout", type=float, default=DEFAULT_TIMEOUT,
                        help=f"per-request timeout in seconds (default {DEFAULT_TIMEOUT})")
    args = parser.parse_args()

    urls = list(args.urls)
    if args.file:
        with open(args.file) as fh:
            urls += [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    urls = urls or DEFAULT_URLS

    print(f"Checking {len(urls)} URLs with up to {min(args.workers, len(urls))} threads "
          f"(timeout {args.timeout}s)...")
    start = time.perf_counter()
    results = check_all(urls, args.workers, args.timeout)
    total = time.perf_counter() - start

    print_status_report(results)
    print_time_report(results)
    print(f"\nTotal wall-clock time: {total:.2f}s")


if __name__ == "__main__":
    main()