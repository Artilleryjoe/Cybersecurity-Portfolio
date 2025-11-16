# Custom Intrusion Detection System (IDS)

## Overview
A modular intrusion detection stack that can scale from a single lab sensor to an enterprise-wide deployment. The repository now ships with:

- A **production blueprint** describing architecture, lifecycle management, and automation expectations (`ENTERPRISE_GUIDE.md`).
- Hardened **Suricata configuration snippets** for multi-threaded packet capture and rich telemetry (`config/suricata-enterprise.yaml`).
- **Custom rule packs** aligned to MITRE ATT&CK® tactics (`rules/local.rules` for labs and `rules/enterprise.rules` for production use cases).
- **Operational scripts** for daily health checks (`scripts/sensor_health_check.sh`).

## Prerequisites
- Snort or Suricata installed
- Network interface or pcap file for testing

## Setup
1. Install your preferred IDS (Snort or Suricata).
2. Copy the rule file from `rules/local.rules` into your IDS rules directory.
3. Start the IDS referencing the custom rule set.
4. Generate or replay traffic to trigger alerts and verify detection.

## Included Rules

### Lab Rules (`rules/local.rules`)
- Telnet, SSH, RDP connection attempts
- HTTP requests for `/admin` pages
- ICMP echo (ping) requests

### Enterprise Rules (`rules/enterprise.rules`)
- Reconnaissance, brute-force, and lateral movement detections
- Command-and-control coverage leveraging JA3/JA3S fingerprints and DNS tunneling heuristics
- SaaS/cloud abuse, exfiltration, and insider-threat monitoring
- OT/ICS protocol visibility and high-fidelity threat-intelligence overrides

## Architecture & Operations

- Review the [Enterprise IDS Blueprint](ENTERPRISE_GUIDE.md) for reference architectures, deployment lifecycle, and runbooks.
- Deploy sensors using the baseline configuration in `config/suricata-enterprise.yaml` and adjust interface affinity, logging, and rule paths for your environment.
- Schedule `scripts/sensor_health_check.sh` via cron or your monitoring platform to confirm packet drops, CPU utilization, and service status remain within thresholds.
- Stream `eve.json` logs to Kafka/Redis or directly into your SIEM for enrichment and response automation.

## Notes
- Tuning false positives and handling high-volume traffic require ongoing adjustment. Use flowbits/detection filters to control noisy detections.
- GitOps-style change control is recommended: lint rules with `suricata -T -S <rule>` before promoting to production bundles.

## Resources
- [Snort Documentation](https://www.snort.org/documents)
