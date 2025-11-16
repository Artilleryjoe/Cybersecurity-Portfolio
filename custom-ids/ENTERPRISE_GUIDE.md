# Enterprise IDS Blueprint

This guide extends the basic lab into a production-grade intrusion detection capability. It focuses on distributed sensor coverage, centralized management, rich telemetry, and automated response.

## 1. Strategic Objectives
- **Full east/west visibility** across data centers, campus, remote workforce, and public cloud segments.
- **Threat-focused detections** that map to MITRE ATT&CK® tactics and support threat-hunting workflows.
- **Operational excellence** through health monitoring, log enrichment, and CI/CD pipelines for rule changes.
- **Integration-first design** that exports enriched events to SIEM, SOAR, and case management platforms.

## 2. Reference Architecture
```
            +----------------------+        +----------------------+
            |  Sensor Cluster A    |        |  Sensor Cluster B    |
            | (DC / Core network)  |        | (Cloud VPC / Branch) |
            +----------+-----------+        +-----------+----------+
                       |                             |
                       v                             v
                +-------------------------------------------+
                |  Message Bus (Kafka / NATS / Redis)       |
                +----------------------+--------------------+
                                       |
                                       v
                        +-------------------------------+
                        | Aggregator / Controller Node  |
                        |  - Suricata rule management   |
                        |  - TLS decryption metadata    |
                        |  - PCAP capture on demand     |
                        +------------------+------------+
                                           |
                                           v
                         +-------------------------------+
                         | SIEM + SOAR + Data Lake       |
                         |  - Correlation + dashboards   |
                         |  - Automation playbooks       |
                         +-------------------------------+
```

## 3. Components
1. **Sensors:** Suricata or Snort inline/IDS nodes with PF_RING/DPDK, managed via Ansible. Sensors push `eve.json` to the message bus.
2. **Controller:** GitOps-backed controller that merges pull requests, compiles rule packs, signs them, and distributes via HTTPS artifact repo.
3. **Message Bus:** Kafka topic per site (`ids.raw`, `ids.enriched`). Schema Registry enforces JSON fields.
4. **Enrichment Workers:** Add asset data, geolocation, TLS JA3, user context, and MITRE tags before forwarding to SIEM.
5. **Analytics Stack:** Elastic/Opensearch or Splunk for dashboards, plus ClickHouse/S3 for long-term forensic PCAP indexes.
6. **Automation:** SOAR platform listens for high-severity alerts, orchestrates firewall blocks or EDR isolation when approved.

## 4. Deployment Lifecycle
1. **Code:** Analysts submit detection pull requests with Suricata rules, Lua scripts, or thresholding policies.
2. **CI Linting:** GitHub Actions (or GitLab CI) run `suricata-update`, `suricata -T`, `yamllint`, and unit tests for Lua/Detect scripts.
3. **Artifact Build:** Approved merge builds a signed rule bundle plus versioned `suricata.yaml`. Artifacts stored in S3 with lifecycle policies.
4. **Distribution:** Controller publishes new bundle to sensors via SaltStack or Ansible. Sensors perform staged reload (canary, 10%, 50%, 100%).
5. **Runtime Validation:** Sensors stream metrics (drops, capture loss, CPU) to Prometheus/Grafana. Alert fatigue tracked via weekly review.

## 5. Security Use Cases
- **Initial Access:** Detect exploit kits, credential phishing, suspicious file downloads, and SMB lateral movement.
- **Execution & Persistence:** Watch for reverse shells, PowerShell remoting, scheduled task creation over WinRM.
- **Privilege Escalation & Defense Evasion:** Monitor Kerberos anomalies, pass-the-hash, and TLS JA3 beacons for Cobalt Strike.
- **Command & Control:** JA3/JA3S heuristics, DNS tunneling, DoH to rare domains, long-duration TLS sessions with low data transfer.
- **Exfiltration:** High-volume uploads to sanctioned SaaS, Rclone user-agents, S3 API abuse, and compressed archive transfers.
- **Insider Threat:** Privileged protocols leaving secure VLANs, unusual OT/ICS traffic, or database dumps during off-hours.

## 6. Operational Runbooks
- **Sensor Health:** Use `scripts/sensor_health_check.sh` daily; integrate with Cron or Prometheus blackbox exporter.
- **Alert Review:** Prioritize `high` severity alerts; ensure each has an owner within ticketing queue.
- **Hunting:** Build saved searches for JA3 fingerprint reuse, repeated 401 responses, and `flowbits`-tagged multi-stage detections.
- **Post-Incident:** Capture PCAP from sensors (use `suricatactl capture`) and store in case folder; annotate correlated alerts in SIEM.

## 7. Roadmap Enhancements
- ML-based anomaly scoring (flow entropy, TLS fingerprint drift).
- Inline prevention mode with automated bypass for OT networks.
- Managed rules ingestion (ET Pro, Proofpoint Emerging Threats) with local overrides.
- Asset-aware policy (per VLAN/per cloud account) driven by CMDB API.

This blueprint, combined with the provided configs, rules, and scripts, forms a production-ready foundation for an enterprise IDS program.
