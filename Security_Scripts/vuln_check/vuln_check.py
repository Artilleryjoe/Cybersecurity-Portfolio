#!/usr/bin/env python3
"""Cross-reference discovered services with curated vulnerability signatures."""

from __future__ import annotations

#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

SEVERITY_ORDER = {"low": 1, "medium": 2, "high": 3, "critical": 4}

SIGNATURES = [
    {
        "name": "BlueKeep RDP",
        "ports": [3389],
        "services": ["rdp", "ms-wbt-server"],
        "cves": ["CVE-2019-0708"],
        "severity": "critical",
        "description": "Unauthenticated RCE in Remote Desktop Services",
        "mitre_attack": ["T1190"],
    },
    {
        "name": "SMB EternalBlue",
        "ports": [445],
        "services": ["microsoft-ds", "smb"],
        "cves": ["CVE-2017-0144"],
        "severity": "critical",
        "description": "SMBv1 remote code execution",
        "mitre_attack": ["T1021"],
    },
    {
        "name": "SSL/TLS Weak Certificates",
        "ports": [443, 8443],
        "services": ["https", "ssl"],
        "cves": ["CVE-2020-0601"],
        "severity": "high",
        "description": "Potential CurveBall certificate spoofing",
        "mitre_attack": ["T1553"],
    },
]


def load_scan(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_services(scan_data: Dict[str, Any]):
    if "open_ports" in scan_data and isinstance(scan_data["open_ports"], list):
        for entry in scan_data["open_ports"]:
            yield {
                "host": scan_data.get("host", "unknown"),
                "port": entry.get("port"),
                "service": (entry.get("service") or "").lower(),
            }
    else:
        for host, info in scan_data.items():
            for entry in info.get("data", []):
                yield {
                    "host": host,
                    "port": entry.get("port"),
                    "service": (entry.get("product") or "").lower(),
                }


def match_signature(service: dict, signature: dict) -> bool:
    port = service.get("port")
    name = service.get("service", "")
    if signature.get("ports") and port not in signature["ports"]:
        return False
    if signature.get("services"):
        return any(alias in name for alias in signature["services"])
    return True


def analyze(scan_data: Dict[str, Any], min_severity: str) -> List[dict]:
    min_rank = SEVERITY_ORDER.get(min_severity.lower(), 1)
    findings: List[dict] = []
    for service in iter_services(scan_data):
        for signature in SIGNATURES:
            if SEVERITY_ORDER.get(signature["severity"], 0) < min_rank:
                continue
            if match_signature(service, signature):
                findings.append(
                    {
                        "host": service["host"],
                        "port": service["port"],
                        "service": service["service"],
                        "signature": signature["name"],
                        "severity": signature["severity"],
                        "cves": signature["cves"],
                        "description": signature["description"],
                        "mitre_attack": signature["mitre_attack"],
                    }
                )
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Cross-reference scan data with curated vulns")
    parser.add_argument("-i", "--input", required=True, type=Path, help="Path to scan JSON file")
    parser.add_argument("-o", "--output", type=Path, help="Optional output JSON path")
    parser.add_argument("--min-severity", default="medium", choices=SEVERITY_ORDER.keys())
    args = parser.parse_args()

    scan_data = load_scan(args.input)
    findings = analyze(scan_data, args.min_severity)

    if args.output:
        args.output.write_text(json.dumps(findings, indent=2), encoding="utf-8")
        print(f"[+] Findings written to {args.output}")
    else:
        print(json.dumps(findings, indent=2))


if __name__ == "__main__":
    main()
