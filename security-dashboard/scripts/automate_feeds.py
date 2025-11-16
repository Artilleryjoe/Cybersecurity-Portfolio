#!/usr/bin/env python3
"""Generate continuous security events for Filebeat ingestion."""
from __future__ import annotations

import argparse
import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict
from urllib import request, error

HOSTS = [
    "10.0.5.21",
    "10.0.5.45",
    "172.16.10.9",
    "192.168.122.15",
]
SERVICES = ["ssh", "rdp", "http", "kubernetes", "vpn"]
VULNS = [
    "CVE-2024-3094",
    "CVE-2023-22527",
    "CVE-2022-1388",
    "CVE-2021-44228",
]
SEVERITIES = ["low", "medium", "high", "critical"]


def build_event() -> Dict[str, str]:
    now = datetime.now(timezone.utc).isoformat()
    host = random.choice(HOSTS)
    service = random.choice(SERVICES)
    severity = random.choice(SEVERITIES)
    event = {
        "host": host,
        "port": random.choice([22, 80, 443, 3389, 6443]),
        "service": service,
        "datasource": "automated-feed",
        "vulnerability": random.choice(VULNS),
        "severity": severity,
        "timestamp": now,
        "tags": ["automated", service, severity],
    }
    return event


def write_events(path: Path, batch: int) -> List[Dict[str, str]]:
    path.parent.mkdir(parents=True, exist_ok=True)
    events = [build_event() for _ in range(batch)]
    with path.open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event) + "\n")
    return events


def push_http(events: List[Dict[str, str]], endpoint: str) -> None:
    payload = "\n".join(json.dumps(event) for event in events).encode("utf-8")
    req = request.Request(endpoint, data=payload, headers={"Content-Type": "application/x-ndjson"})
    try:
        with request.urlopen(req, timeout=5) as resp:
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    destination = Path(args.output)
    while True:
        events = write_events(destination, args.batch)
        print(f"wrote {len(events)} events to {destination}")
        if args.logstash_endpoint:
            push_http(events, args.logstash_endpoint)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
