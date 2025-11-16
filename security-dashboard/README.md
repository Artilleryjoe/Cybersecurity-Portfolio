# Security Dashboard - Base Setup
## Overview
This repository contains the foundational setup for a custom security dashboard using the Elastic Stack (Elasticsearch and Kibana). It provides a minimal single-node environment, suitable for proofs of concept, to visualize vulnerability scan data and network security metrics in an intuitive web interface. In professional deployments, the stack typically runs across multiple nodes with security features enabled.

## Components
- Elasticsearch: Stores and indexes security scan documents
- Kibana: Provides the visualization and dashboard interface
- Index: security-scans with fields for host, port, service, vulnerability, and timestamp

# Getting Started
## Prerequisites
- Docker & Docker Compose installed
- Basic familiarity with Elasticsearch and Kibana
- curl or any HTTP client to ingest sample data

## Steps
Launch Elasticsearch and Kibana containers:

```bash
docker-compose up -d
```

## Verify Elasticsearch and Kibana are running:

Elasticsearch: http://localhost:9200

Kibana: http://localhost:5601

- Create the security-scans index with proper mapping (if needed).

Ingest sample security scan data:

```bash
curl -X POST "localhost:9200/security-scans/_doc/" -H 'Content-Type: application/json' -d'
{
  "host": "192.168.1.100",
  "port": 22,
  "service": "ssh",
  "vulnerability": "CVE-2025-0001",
  "timestamp": "2025-07-25T17:00:00"
}'
```
- In Kibana, create a data view on security-scans and set timestamp as the time field.
- Build visualizations and dashboards based on your scan data.

## Notes
- Use .keyword fields for aggregation in visualizations (e.g., vulnerability.keyword).
- Refresh the field list in Kibana if new fields aren’t showing.
- This is a base setup; further ingestion automation and dashboards will be developed.

## Custom Security Dashboard

### Scope
Real-time visualization of security events and metrics with a path toward enterprise-scale dashboards.

### Tools
- Grafana
- Kibana
- Custom data sources

### Implementation
1. Install visualization tools.
2. Connect to log and data streams.
3. Build visualizations and alerting.

### Challenges
- Data parsing
- Real-time ingestion
- Uptime

### Next Steps
- Automate data feeds ✅
- Configure alerts ✅
- Plan for enterprise-level scaling ✅
- Add Logstash and Beats pipelines for structured ingest ✅
- Enable TLS and role-based access control ✅
- Implement index lifecycle management and snapshots ✅

## Automated Data Feeds
Use the included Python helper to generate normalized events that Filebeat can forward to Logstash.

```bash
python3 scripts/automate_feeds.py --batch 25 --interval 3 \\
  --logstash-endpoint https://localhost:9601
```

- The script appends newline-delimited JSON to `data/feeds/security-events.log`.
- Filebeat (configured in `beats/filebeat.yml`) tails the file and sends events over TLS to Logstash.
- If the optional `--logstash-endpoint` is set, events are also pushed to the HTTPS Logstash input for SOAR integrations.

## Logstash and Beats Pipelines
- `logstash/pipeline/security.conf` normalizes timestamps, adds metadata, and writes into `security-scans-*` indices.
- `logstash/config/logstash.yml` enables persistent queues plus TLS-secured monitoring against Elasticsearch.
- `beats/filebeat.yml` defines a filestream input and disables ILM so Logstash/Elasticsearch manage lifecycle policies.
- Update Filebeat fields or add new inputs for additional scanners while keeping the same Logstash output stanza.

## TLS and Role-Based Access Control
TLS is now required between every component. Generate certificates before starting Docker Compose by following `certs/README.md`.

1. Create `.env` with stack credentials:

```
ELASTIC_PASSWORD=changeme
ELASTIC_USER=elastic
LOGSTASH_USER=logstash_writer
LOGSTASH_PASSWORD=logstash_writer_password
```

2. Bootstrap users and roles once Elasticsearch is up:

```bash
curl -u elastic:$ELASTIC_PASSWORD --cacert certs/ca.crt \\
  -X POST https://localhost:9200/_security/role/logstash_writer -H 'Content-Type: application/json' -d '{
    "cluster": ["monitor", "manage_index_templates", "manage_ilm"],
    "indices": [{"names": ["security-scans-*"], "privileges": ["write", "create_index"]}]
  }'

curl -u elastic:$ELASTIC_PASSWORD --cacert certs/ca.crt \\
  -X POST https://localhost:9200/_security/user/logstash_writer -H 'Content-Type: application/json' -d '{
    "password": "'$LOGSTASH_PASSWORD'",
    "roles": ["logstash_writer"],
    "full_name": "Logstash Output"
  }'
```

3. Kibana enforces TLS for the UI (`https://localhost:5601`). Use the built-in `elastic` superuser for bootstrap, then create analyst roles scoped to required data views.

## Alerting
- Import `scripts/alerts/critical-vulnerability-watcher.json` in **Stack Management → Watcher** to log when critical findings arrive.
- Kibana Security Solution detection rules can also be created to send email/Webhook/PagerDuty notifications.
- Because Logstash exposes an HTTPS HTTP input on port `9601`, external SOAR tooling can push enrichment data using mutual TLS.

## Index Lifecycle Management & Snapshots
`scripts/ilm_and_snapshots.sh` creates an ILM policy, index template, snapshot repository, and an initial snapshot.

```bash
chmod +x scripts/ilm_and_snapshots.sh
ES_PASS=$ELASTIC_PASSWORD ./scripts/ilm_and_snapshots.sh \
  ES_URL=https://localhost:9200 ES_USER=elastic CACERT=certs/ca.crt
```

- ILM stages follow a hot/warm/cold/delete progression (7/30/90 days by default).
- Snapshots write to the `snapshots` Docker volume (`/usr/share/elasticsearch/snapshots`). Point this to an object store in production.

## Enterprise-Level Scaling
See `scripts/architecture.md` for a detailed roadmap that covers ingest horizontal scaling, Kafka buffering, RBAC, observability, and DR patterns.

### Professional ELK Stack Comparison

| Feature | Base Setup | Professional Deployment |
|--------|------------|-------------------------|
| Topology | Single-node Elasticsearch and Kibana | Multi-node clusters with load balancers |
| Ingestion | Manual curl or custom scripts | Beats agents feeding Logstash pipelines |
| Security | xpack security disabled | TLS encryption and role-based access control |
| Management | Ad-hoc indices | Index lifecycle management and snapshot backups |
| Monitoring | Manual checks | Centralized monitoring and alerting with X-Pack |

### Resources
- [Grafana Docs](https://grafana.com/docs/)

## License & Disclaimer
This project is for educational and authorized professional use only. Do not use on unauthorized networks or systems.
