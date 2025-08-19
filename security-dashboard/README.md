# Security Dashboard - Base Setup
## Overview
This repository contains the foundational setup for a custom security dashboard using the Elastic Stack (Elasticsearch and Kibana). It is designed for solo cybersecurity practitioners to visualize vulnerability scan data and network security metrics in an intuitive web interface.

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
=======
Real-time visualization of security events and metrics.


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
- Automate data feeds
- Configure alerts
- Plan for enterprise-level scaling

### Resources
- [Grafana Docs](https://grafana.com/docs/)

## License & Disclaimer
This project is for educational and authorized professional use only. Do not use on unauthorized networks or systems.

