#!/usr/bin/env python3
"""Generate normalized JSON events for the security dashboard."""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List
from urllib import error, request

HOSTS = [
    "10.0.5.21",
    "10.0.5.45",
    "172.16.10.9",
    "192.168.122.15",
]
PORTS = [22, 80, 443, 3389, 6443]
SERVICES = ["ssh", "rdp", "http", "kubernetes", "vpn"]
VULNS = [
    "CVE-2024-3094",
    "CVE-2023-22527",
    "CVE-2022-1388",
    "CVE-2021-44228",
]
SEVERITIES = ["low", "medium", "high", "critical"]


@dataclass
class FeedEvent:
    host: str
    port: int
    service: str
    datasource: str
    vulnerability: str
    severity: str
    timestamp: str
    tags: List[str]

    def to_json(self) -> str:
        return json.dumps(asdict(self))


def build_event(rng: random.Random) -> FeedEvent:
    now = datetime.now(timezone.utc).isoformat()
    service = rng.choice(SERVICES)
    severity = rng.choice(SEVERITIES)
    return FeedEvent(
        host=rng.choice(HOSTS),
        port=rng.choice(PORTS),
        service=service,
        datasource="automated-feed",
        vulnerability=rng.choice(VULNS),
        severity=severity,
        timestamp=now,
        tags=["automated", service, severity],
    )


def write_events(path: Path, events: Iterable[FeedEvent]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(event.to_json() + "\n")


def push_http(events: Iterable[FeedEvent], endpoint: str, timeout: float) -> None:
    payload = "\n".join(event.to_json() for event in events).encode("utf-8")
    req = request.Request(endpoint, data=payload, headers={"Content-Type": "application/x-ndjson"})
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            resp.read()
    except error.URLError as exc:
        print(f"[warn] Failed to push events to {endpoint}: {exc}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automate security event feed generation")
    parser.add_argument(
        "--output",
        default="data/feeds/security-events.log",
        help="Path to the log file monitored by Filebeat",
    )
    parser.add_argument("--batch", type=int, default=10, help="Number of events to create per cycle")
    parser.add_argument("--interval", type=float, default=5.0, help="Seconds to sleep between batches")
    parser.add_argument(
        "--logstash-endpoint",
        default="",
        help="Optional https endpoint (https://host:9601) for posting NDJSON events directly",
    )
    parser.add_argument("--max-cycles", type=int, default=0, help="Number of batches to produce before exiting (0=infinite)")
    parser.add_argument("--seed", type=int, help="Optional RNG seed for deterministic runs")
    parser.add_argument("--stdout", action="store_true", help="Also print NDJSON events to stdout")
    parser.add_argument("--http-timeout", type=float, default=5.0, help="HTTP push timeout in seconds")
    return parser.parse_args()


def run_cycles(args: argparse.Namespace) -> None:
    rng = random.Random(args.seed)
    destination = Path(args.output)
    cycle = 0
    while True:
        events = [build_event(rng) for _ in range(args.batch)]
        write_events(destination, events)
        print(f"[feed] wrote {len(events)} events to {destination}")
        if args.stdout:
            for event in events:
                print(event.to_json())
        if args.logstash_endpoint:
            push_http(events, args.logstash_endpoint, args.http_timeout)
        cycle += 1
        if args.max_cycles and cycle >= args.max_cycles:
            break
        time.sleep(max(args.interval, 0.1))


def main() -> None:
    args = parse_args()
    try:
        run_cycles(args)
    except KeyboardInterrupt:
        print("[feed] interrupted by user", file=sys.stderr)


if __name__ == "__main__":
    main()
