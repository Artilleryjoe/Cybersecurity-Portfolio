# Security Dashboard Architecture & Scaling Plan

## Current Footprint
- Single Elasticsearch node used for storage and search
- Kibana for visualization
- Optional Logstash + Filebeat tier for normalized ingest

## Automated Data Feeds
1. Filebeat tails `data/feeds/security-events.log` and forwards data over TLS to Logstash.
2. Logstash enforces schema, adds metadata, and writes into `security-scans-*` indices.
3. `scripts/automate_feeds.py` produces continuous synthetic data to simulate scanner output or can be wired to existing scanners by replacing the event generator.

## Alerting Strategy
- Kibana Detection Rules for severity thresholds and frequency of findings.
- Watcher (see `scripts/alerts/critical-vulnerability-watcher.json`) for SLA-style alerting integrated with ticketing webhooks.
- Use the HTTP input on Logstash to accept alert enrichment payloads from SOAR platforms.

## Enterprise-Scale Roadmap
1. **Data Tier**
   - Promote Elasticsearch to a 3 master / 2 data node cluster with dedicated ingest nodes for heavy parsing.
   - Enable cross-cluster replication for DR and search.
   - Use hot/warm/cold architecture that aligns with ILM policy defined in `scripts/ilm_and_snapshots.sh`.
2. **Ingest Tier**
   - Horizontal scale Logstash with a load balancer in front of Beats traffic.
   - Introduce Kafka between Beats and Logstash for burst absorption and replay.
3. **Security**
   - Mandatory TLS everywhere using certificate authority stored in HashiCorp Vault.
   - RBAC enforced via Elastic built-in roles plus SAML/LDAP federation for analysts.
4. **Observability**
   - Use Elastic Fleet for Beat lifecycle management and to track agent health.
   - Ship Elastic metrics into Prometheus/Grafana for SLO dashboards.
5. **Resilience**
   - Hourly snapshots to an object storage repository (S3, GCS, or MinIO) with retention policy managed by ILM.
   - Test snapshot restore quarterly using automation pipeline.

## Deployment Guardrails
- All secrets supplied via `.env` or an orchestrator such as Kubernetes secrets.
- Terraform or Ansible should manage infrastructure for repeatability.
- GitOps workflow keeps configuration-as-code in this repository to enable reviews.
