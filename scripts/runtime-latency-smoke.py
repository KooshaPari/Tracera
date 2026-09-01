#!/usr/bin/env python3
"""Bounded, secret-free latency smoke for a local Tracera runtime.

The script intentionally uses only the Python standard library so it can run
on a clean release host. It exercises representative read paths and never
writes data or contacts a non-loopback host unless BASE_URL is explicitly
provided by the caller.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

DEFAULT_PATHS = ("/health", "/ready", "/", "/evidence", "/sdlc-pm/sprints")


@dataclass(frozen=True)
class Sample:
    path: str
    elapsed_ms: float
    status: int | None
    error: str | None = None


def fetch(base_url: str, path: str, timeout: float) -> Sample:
    started = time.perf_counter()
    try:
        request = Request(f"{base_url.rstrip('/')}{path}", headers={"Accept": "application/json"})
        with urlopen(request, timeout=timeout) as response:
            response.read(4096)
            status = response.status
        return Sample(path, (time.perf_counter() - started) * 1000, status)
    except HTTPError as exc:
        return Sample(path, (time.perf_counter() - started) * 1000, exc.code, f"http_{exc.code}")
    except (URLError, TimeoutError, OSError) as exc:
        return Sample(path, (time.perf_counter() - started) * 1000, None, type(exc).__name__)


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((len(ordered) - 1) * fraction))
    return ordered[index]


def run(args: argparse.Namespace) -> dict[str, object]:
    paths = tuple(args.paths or ()) or DEFAULT_PATHS
    warmup_deadline = time.monotonic() + args.warmup
    while time.monotonic() < warmup_deadline:
        fetch(args.base_url, paths[0], args.timeout)
        time.sleep(0.02)

    samples: list[Sample] = []
    lock = threading.Lock()

    def request(index: int) -> Sample:
        sample = fetch(args.base_url, paths[index % len(paths)], args.timeout)
        with lock:
            samples.append(sample)
        return sample

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(request, index) for index in range(args.requests)]
        for future in as_completed(futures):
            future.result()
    elapsed_s = time.perf_counter() - started

    latencies = [sample.elapsed_ms for sample in samples]
    failures = [sample for sample in samples if sample.status is None or sample.status >= 500]
    client_errors = [sample for sample in samples if sample.status is not None and 400 <= sample.status < 500]
    return {
        "base_url": args.base_url,
        "requests": len(samples),
        "concurrency": args.concurrency,
        "duration_seconds": round(elapsed_s, 3),
        "requests_per_second": round(len(samples) / elapsed_s, 2) if elapsed_s else 0.0,
        "latency_ms": {
            "p50": round(percentile(latencies, 0.50), 2),
            "p95": round(percentile(latencies, 0.95), 2),
            "p99": round(percentile(latencies, 0.99), 2),
            "max": round(max(latencies), 2) if latencies else 0.0,
        },
        "failures": len(failures),
        "client_errors": len(client_errors),
        "status_counts": dict(Counter(str(sample.status) for sample in samples)),
        "error_counts": dict(Counter(sample.error for sample in samples if sample.error)),
        "paths": list(paths),
        "thresholds": {
            "p95_ms": args.p95_threshold_ms,
            "max_ms": args.max_threshold_ms,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=os.environ.get("BASE_URL", "http://127.0.0.1:8080"))
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--requests", type=int, default=80)
    parser.add_argument("--warmup", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument(
        "--p95-threshold-ms",
        type=float,
        default=float(os.environ.get("TRACERA_LATENCY_P95_MS", "0")),
        help="fail when p95 exceeds this value; 0 disables the threshold",
    )
    parser.add_argument(
        "--max-threshold-ms",
        type=float,
        default=float(os.environ.get("TRACERA_LATENCY_MAX_MS", "0")),
        help="fail when max latency exceeds this value; 0 disables the threshold",
    )
    parser.add_argument("--path", dest="paths", action="append", help="path to exercise (repeatable)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    parsed = urlparse(args.base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
        parser.error("base-url must be an http(s) URL without embedded credentials")
    if any(char in args.base_url for char in ("\n", "\r", "\t")):
        parser.error("base-url contains control characters")
    if (
        args.concurrency < 1
        or args.requests < 1
        or args.warmup < 0
        or args.timeout <= 0
        or args.p95_threshold_ms < 0
        or args.max_threshold_ms < 0
    ):
        parser.error("concurrency/requests must be positive; warmup and thresholds must be non-negative")
    result = run(args)
    latency = result["latency_ms"]
    threshold_failures = []
    if args.p95_threshold_ms and latency["p95"] > args.p95_threshold_ms:
        threshold_failures.append(
            f"p95 {latency['p95']:.2f}ms > {args.p95_threshold_ms:.2f}ms"
        )
    if args.max_threshold_ms and latency["max"] > args.max_threshold_ms:
        threshold_failures.append(
            f"max {latency['max']:.2f}ms > {args.max_threshold_ms:.2f}ms"
        )
    result["threshold_failures"] = threshold_failures
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(
            "runtime latency smoke: "
            f"{result['requests']} requests @ c={result['concurrency']}, "
            f"p50={latency['p50']}ms p95={latency['p95']}ms "
            f"rps={result['requests_per_second']} failures={result['failures']} "
            f"4xx={result['client_errors']}"
        )
        if threshold_failures:
            print("latency threshold: FAIL: " + "; ".join(threshold_failures), file=sys.stderr)
    return 1 if result["failures"] or threshold_failures else 0


if __name__ == "__main__":
    sys.exit(main())
