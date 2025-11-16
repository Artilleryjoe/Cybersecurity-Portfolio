#!/usr/bin/env python3
"""Generate repository-aware sample events for the enterprise security dashboard."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = DASHBOARD_ROOT / "data" / "ingest" / "enterprise-events.jsonl"


def _utc_timestamp(minutes_ago: int = 0) -> str:
    ts = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def _list_dirs(path: Path) -> List[str]:
    if not path.exists():
        return []
    return sorted([p.name for p in path.iterdir() if p.is_dir() and not p.name.startswith(".")])


def _extract_rule_examples(rule_files: List[Path]) -> List[Tuple[str, str]]:
    examples: List[Tuple[str, str]] = []
    for rule_file in rule_files:
        if not rule_file.exists():
            continue
        for line in rule_file.read_text().splitlines():
            if "msg:" in line and "sid:" in line:
                msg_match = re.search(r'msg:\"([^\"]+)\"', line)
                sid_match = re.search(r'sid:(\d+)', line)
                if msg_match and sid_match:
                    examples.append((sid_match.group(1), msg_match.group(1)))
            if len(examples) >= 4:
                return examples
    return examples


def _collect_metadata() -> Dict[str, object]:
    security_scripts_dir = REPO_ROOT / "Security_Scripts"
    ids_rules_dir = REPO_ROOT / "custom-ids" / "rules"
    ansible_playbooks_dir = REPO_ROOT / "ansible-hardening" / "playbooks"
    blockchain_dir = REPO_ROOT / "blockchain-secure-logging"
    quantum_dir = REPO_ROOT / "quantum-computing"

    metadata: Dict[str, object] = {
        "security_scripts": _list_dirs(security_scripts_dir),
        "ids_rule_files": [p.name for p in ids_rules_dir.glob("*.rules")],
        "ansible_playbooks": [p.name for p in ansible_playbooks_dir.glob("*.yml")],
        "blockchain_components": _list_dirs(blockchain_dir),
        "quantum_documents": [p.name for p in quantum_dir.glob("*.md")],
    }
    metadata["security_scripts_count"] = len(metadata["security_scripts"])  # type: ignore[index]
    metadata["ansible_playbook_count"] = len(metadata["ansible_playbooks"])  # type: ignore[index]
    metadata["blockchain_component_count"] = len(metadata["blockchain_components"])  # type: ignore[index]
    metadata["quantum_document_count"] = len(metadata["quantum_documents"])  # type: ignore[index]
    metadata["ids_rule_file_count"] = len(metadata["ids_rule_files"])  # type: ignore[index]
    metadata["ids_rule_examples"] = _extract_rule_examples(
        [ids_rules_dir / name for name in metadata["ids_rule_files"]]  # type: ignore[index]
    )
    return metadata


def _build_events(metadata: Dict[str, object]) -> List[Dict[str, object]]:
    events: List[Dict[str, object]] = []

    recon_scripts = metadata.get("security_scripts", [])
    recon_tool = recon_scripts[0] if recon_scripts else "Security_Scripts/port-scanner"

    events.append(
        {
            "target_index": "security-scans",
            "timestamp": _utc_timestamp(5),
            "host": "10.20.5.17",
            "tool": f"Security_Scripts/{recon_tool}",
            "service": "https",
            "port": 443,
            "finding": "443/tcp open with weak ciphers",
            "severity": "medium",
            "tags": ["recon", "tls", "automated"],
            "source_reference": f"Security_Scripts/{recon_tool}",
        }
    )

    events.append(
        {
            "target_index": "security-scans",
            "timestamp": _utc_timestamp(4),
            "host": "10.20.8.44",
            "tool": "Security_Scripts/vuln_check",
            "vulnerability": "CVE-2024-34985",
            "cvss": 8.1,
            "status": "exploitable",
            "severity": "high",
            "tags": ["cve", "exploit_checker"],
            "source_reference": "Security_Scripts/vuln_check",
        }
    )

    rule_examples: List[Tuple[str, str]] = metadata.get("ids_rule_examples", [])  # type: ignore[assignment]
    rule_sid, rule_msg = rule_examples[0] if rule_examples else ("2100200", "ETP C2 Suspicious JA3 CobaltStrike")
    events.append(
        {
            "target_index": "ids-alerts",
            "timestamp": _utc_timestamp(3),
            "sensor": "custom-ids/suricata01",
            "rule_id": int(rule_sid),
            "rule_name": rule_msg,
            "src_ip": "192.0.2.77",
            "dest_ip": "10.200.4.16",
            "dest_port": 443,
            "severity": "critical",
            "tags": ["c2", "mitre-command-and-control"],
            "source_reference": "custom-ids/rules/enterprise.rules",
        }
    )

    events.append(
        {
            "target_index": "ids-alerts",
            "timestamp": _utc_timestamp(2),
            "sensor": "custom-ids/suricata02",
            "rule_id": 2100801,
            "rule_name": "ETP OT BACnet writeProperty",
            "src_ip": "10.1.50.8",
            "dest_ip": "10.60.24.9",
            "dest_port": 47808,
            "severity": "high",
            "tags": ["ot", "bacnet", "lateral"],
            "source_reference": "custom-ids/rules/enterprise.rules",
        }
    )

    events.append(
        {
            "target_index": "ansible-compliance",
            "timestamp": _utc_timestamp(10),
            "host": "linux-bastion-01",
            "playbook": "ansible-hardening/playbooks/hardening.yml",
            "control": "cis_2_2_enable_firewalld",
            "status": "pass",
            "severity": "medium",
            "tags": ["cis", "rhel8"],
            "details": "firewalld running",
        }
    )

    events.append(
        {
            "target_index": "ansible-compliance",
            "timestamp": _utc_timestamp(9),
            "host": "linux-bastion-02",
            "playbook": "ansible-hardening/playbooks/hardening.yml",
            "control": "cis_5_1_auditd_config",
            "status": "fail",
            "severity": "high",
            "tags": ["cis", "auditd"],
            "details": "max_log_file_action set to keep_logs",
        }
    )

    events.append(
        {
            "target_index": "blockchain-audit",
            "timestamp": _utc_timestamp(6),
            "ledger": "blockchain-secure-logging",
            "tx_id": "0x8a2f9b7c8d",
            "status": "anchored",
            "chain": "ethereum-goerli",
            "hash": "f6c1b8f1e4f83d50e6c35a5d88777d1a",
            "evidence_batch": _utc_timestamp(6)[:13],
            "source_reference": "blockchain-secure-logging/onchain",
        }
    )

    events.append(
        {
            "target_index": "mobile-findings",
            "timestamp": _utc_timestamp(25),
            "application": "com.example.securebank",
            "report": "mobile-security-analysis/analyze_apk.py",
            "risk_score": 72,
            "severity": "medium",
            "issues": ["Weak certificate pinning", "Debug flag enabled"],
            "tags": ["android", "static-analysis"],
        }
    )

    events.append(
        {
            "target_index": "quantum-research",
            "timestamp": _utc_timestamp(30),
            "experiment": "QRNGSteganography.md",
            "metric": "entropy_bits_per_byte",
            "value": 7.94,
            "severity": "info",
            "notes": "QRNG output embedded in surveillance image passed all NIST SP800-22 tests",
            "source_reference": "quantum-computing/QRNGSteganography.md",
        }
    )

    events.append(
        {
            "target_index": "platform-inventory",
            "timestamp": _utc_timestamp(),
            "component": "repository-health",
            "security_scripts": metadata.get("security_scripts_count", 0),
            "ids_rule_files": metadata.get("ids_rule_file_count", 0),
            "ansible_playbooks": metadata.get("ansible_playbook_count", 0),
            "mobile_analyzers": 1 if (REPO_ROOT / "mobile-security-analysis" / "analyze_apk.py").exists() else 0,
            "blockchain_components": metadata.get("blockchain_component_count", 0),
            "quantum_documents": metadata.get("quantum_document_count", 0),
            "notes": "Auto-generated by scripts/build_enterprise_dataset.py",
        }
    )

    return events


def _write_events(events: List[Dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event))
            handle.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to the JSON Lines file to generate")
    args = parser.parse_args()

    metadata = _collect_metadata()
    events = _build_events(metadata)
    _write_events(events, args.output)
    print(f"Wrote {len(events)} events to {args.output}")


if __name__ == "__main__":
    main()
