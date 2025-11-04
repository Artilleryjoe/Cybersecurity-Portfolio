#!/usr/bin/env python3
"""Command line utility for querying the Shodan API.

The original implementation executed API calls at import time which made the
module impossible to reuse and difficult to test.  The code has been rewritten
so that it now exposes small, testable functions and only performs network
operations when ``main`` is invoked.  The script also accepts a configurable
delay between API calls to help respect Shodan's rate limits.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Iterable, List

try:
    import shodan
except ModuleNotFoundError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "The 'shodan' package is required to run this script. Install it with 'pip install shodan'."
    ) from exc


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Return parsed command line arguments."""

    parser = argparse.ArgumentParser(
        description="Scan targets with the Shodan API and retrieve exposed services."
    )
    parser.add_argument("-k", "--apikey", required=True, help="Your Shodan API key")
    parser.add_argument("-i", "--input", required=True, help="Path to file with list of target IPs")
    parser.add_argument(
        "-o",
        "--output",
        default="shodan_output.json",
        help="Output JSON file (default: shodan_output.json)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API calls in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--banner-length",
        type=int,
        default=100,
        help="Maximum number of characters to store from each service banner",
    )
    return parser.parse_args(argv)


def load_targets(path: Path) -> List[str]:
    """Load target IP addresses from a newline-delimited file."""

    if not path.exists():
        raise SystemExit(f"Input file '{path}' does not exist")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def query_host(api: shodan.Shodan, ip: str, banner_length: int) -> Dict[str, object]:
    """Retrieve host information from Shodan."""

    host = api.host(ip)
    result: Dict[str, object] = {
        "ip": host.get("ip_str"),
        "org": host.get("org", "N/A"),
        "os": host.get("os", "N/A"),
        "ports": host.get("ports", []),
        "data": [],
        "vulns": host.get("vulns", []),
    }

    for item in host.get("data", []):
        banner = item.get("data", "") or ""
        result["data"].append(
            {
                "port": item.get("port"),
                "transport": item.get("transport"),
                "product": item.get("product"),
                "version": item.get("version"),
                "banner": banner[:banner_length],
            }
        )

    return result


def scan_targets(
    api: shodan.Shodan,
    targets: Iterable[str],
    *,
    banner_length: int,
    delay: float,
) -> Dict[str, object]:
    """Scan each target and return a mapping of results."""

    results: Dict[str, object] = {}
    for ip in targets:
        try:
            print(f"[+] Querying Shodan for {ip}...")
            results[ip] = query_host(api, ip, banner_length)
        except shodan.APIError as exc:
            print(f"[-] Error retrieving data for {ip}: {exc}")
            results[ip] = {"error": str(exc)}

        if delay > 0:
            time.sleep(delay)

    return results


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv)
    targets = load_targets(Path(args.input))
    if not targets:
        raise SystemExit("No targets found in the input file")

    api = shodan.Shodan(args.apikey)
    results = scan_targets(
        api,
        targets,
        banner_length=max(args.banner_length, 0),
        delay=max(args.delay, 0.0),
    )

    output_path = Path(args.output)
    output_path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[+] Scan complete. Results saved to {output_path}")


if __name__ == "__main__":
    main()
