#!/usr/bin/env python3
"""vuln_check.py
Match discovered services and versions to a small CVE list.

The script expects JSON input produced by scanners such as shodan-scanner.py.
Example format:
{
    "198.51.100.23": {
        "data": [
            {"port": 80, "product": "Apache httpd", "version": "2.4.41"},
            {"port": 22, "product": "OpenSSH", "version": "7.4"}
        ]
    }
}
"""

import argparse
import json
from typing import Dict, List

# Simple built-in vulnerability database.
# Keys are "<product> <version>" in lowercase.
VULN_DB: Dict[str, List[str]] = {
    "apache httpd 2.4.41": ["CVE-2021-41773", "CVE-2021-42013"],
    "nginx 1.18.0": ["CVE-2021-23017"],
    "openssh 7.4": ["CVE-2018-15473"],
}


def load_input(path: str) -> Dict:
    """Load JSON scan results from *path*."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def match_cves(scan_data: Dict) -> List[Dict[str, str]]:
    """Return a list of vulnerable services with CVE matches."""
    results: List[Dict[str, str]] = []
    for host, info in scan_data.items():
        services = info.get("data", [])
        for service in services:
            product = service.get("product")
            version = service.get("version")
            port = service.get("port")
            if not (product and version):
                continue
            key = f"{product.lower()} {version.lower()}"
            cves = VULN_DB.get(key)
            if cves:
                results.append(
                    {
                        "host": host,
                        "port": port,
                        "service": product,
                        "version": version,
                        "cves": cves,
                    }
                )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Match discovered service versions against a local CVE list"
    )
    parser.add_argument(
        "-i", "--input", required=True, help="JSON file with service scan data"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Optional JSON file to save vulnerability matches",
    )

    args = parser.parse_args()

    data = load_input(args.input)
    matches = match_cves(data)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(matches, f, indent=4)
        print(f"[+] Results saved to {args.output}")
    else:
        print(json.dumps(matches, indent=4))


if __name__ == "__main__":
    main()
