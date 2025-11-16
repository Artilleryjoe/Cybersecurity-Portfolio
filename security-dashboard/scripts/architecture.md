# Enterprise Security Dashboard Architecture

## High-level flow
1. **Producers** – Every capability inside `Cybersecurity-Portfolio/` emits JSON (newline delimited).  Examples include:
   - `Security_Scripts/port-scanner` and `Security_Scripts/vuln_check` exporting recon results.
   - `custom-ids/` Suricata deployments forwarding EVE JSON that references the curated `enterprise.rules` pack.
   - `ansible-hardening/playbooks` summarizing CIS control status.
   - `blockchain-secure-logging/` reporting anchoring transactions.
   - `mobile-security-analysis/analyze_apk.py` rating APKs.
   - Research notes under `quantum-computing/` for QRNG or post-quantum experiments.
2. **Landing zone (`data/ingest/`)** – Tools drop JSON Lines artifacts in the shared folder.  Field names follow the schema used in `scripts/build_enterprise_dataset.py` so that Logstash can route to the proper index.
3. **Logstash** – The pipeline defined in `logstash/pipeline/logstash.conf` ingests the JSON Lines files and accepts Beats streams on port `5044`.  It adds `@metadata.target_index` from the `target_index` field and ships the documents to Elasticsearch.
4. **Elasticsearch** – Stores time-series indices per capability (`security-scans-*`, `ids-alerts-*`, `ansible-compliance-*`, `blockchain-audit-*`, `mobile-findings-*`, `quantum-research-*`, and `platform-inventory-*`).
5. **Visualization** – Kibana consumes the indices through the saved objects in `kibana/`.  Grafana connects via the provisioned datasource in `grafana/provisioning/datasources/datasource.yml` to power SRE dashboards.

## Index mapping strategy
- **security-scans** – Recon/vulnerability data. Key fields: `host`, `port`, `tool`, `vulnerability`, `severity`, `tags`.
- **ids-alerts** – Suricata/Snort alerts tied to `custom-ids/rules`. Key fields: `rule_id`, `rule_name`, `sensor`, `src_ip`, `dest_ip`, `severity`.
- **ansible-compliance** – Outputs from CIS playbooks. Key fields: `host`, `control`, `status`, `severity`, `playbook`.
- **blockchain-audit** – Anchor confirmations produced by `blockchain-secure-logging`. Key fields: `tx_id`, `chain`, `status`, `hash`.
- **mobile-findings** – APK analysis metadata. Key fields: `application`, `risk_score`, `issues`, `severity`.
- **quantum-research** – Research telemetry from `quantum-computing/`. Key fields: `experiment`, `metric`, `value`, `notes`.
- **platform-inventory** – Automatically generated inventory of repository assets (script counts, rule counts, etc.) to monitor coverage.

## Deployment considerations
- **Scale-out** – Pin each component to a dedicated node or orchestrator pod.  Enable Elasticsearch snapshots, configure ILM policies, and attach security realms.
- **Data onboarding** – Replace the file input with Kafka, HTTP, or S3 modules once telemetry volume exceeds the sample dataset.  Beats agents can ship EVE JSON directly to Logstash by targeting port `5044`.
- **Automation hooks** –
  - Extend CI jobs for `Security_Scripts/` to emit JSON Lines into `data/ingest/` whenever scans finish.
  - Add a post-task handler to the `ansible-hardening` playbooks that posts compliance status to the Beats port using `uri`.
  - Chain `blockchain-secure-logging/offchain` workers so every notarized batch is surfaced in the `blockchain-audit-*` index.
- **Dashboards** – Use Kibana Lens or Grafana panels to plot severity trends, MITRE ATT&CK® coverage, compliance drift, and ledger confirmation latency.  The blueprint JSON files included here describe panel placement and the metrics required from each index.

