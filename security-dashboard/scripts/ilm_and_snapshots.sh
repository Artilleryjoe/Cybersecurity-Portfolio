#!/usr/bin/env bash
set -euo pipefail

ES_URL=${ES_URL:-https://localhost:9200}
ES_USER=${ES_USER:-elastic}
ES_PASS=${ES_PASS:-changeme}
ILM_POLICY=${ILM_POLICY:-security-scan-lifecycle}
INDEX_TEMPLATE=${INDEX_TEMPLATE:-security-scans-template}
SNAPSHOT_REPO=${SNAPSHOT_REPO:-security-snapshots}
CACERT=${CACERT:-certs/ca.crt}

if [ ! -f "$CACERT" ]; then
  echo "CA certificate $CACERT not found. Pass CACERT=/path/to/ca.crt" >&2
  exit 1
fi

echo "Creating ILM policy $ILM_POLICY"
curl -s -u "$ES_USER:$ES_PASS" --cacert "$CACERT" -X PUT "$ES_URL/_ilm/policy/$ILM_POLICY" -H 'Content-Type: application/json' -d @- <<POLICY
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_age": "7d",
            "max_size": "25gb"
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "forcemerge": {"max_num_segments": 1},
          "shrink": {"number_of_shards": 1}
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "freeze": {}
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
POLICY

echo "Creating composable template $INDEX_TEMPLATE"
curl -s -u "$ES_USER:$ES_PASS" --cacert "$CACERT" -X PUT "$ES_URL/_index_template/$INDEX_TEMPLATE" -H 'Content-Type: application/json' -d @- <<TEMPLATE
{
  "index_patterns": ["security-scans-*"],
  "template": {
    "settings": {
      "index.lifecycle.name": "$ILM_POLICY",
      "index.lifecycle.rollover_alias": "security-scans"
    }
  },
  "priority": 500
}
TEMPLATE

echo "Creating snapshot repository $SNAPSHOT_REPO"
curl -s -u "$ES_USER:$ES_PASS" --cacert "$CACERT" -X PUT "$ES_URL/_snapshot/$SNAPSHOT_REPO" -H 'Content-Type: application/json' -d @- <<REPO
{
  "type": "fs",
  "settings": {
    "location": "/usr/share/elasticsearch/snapshots",
    "compress": true
  }
}
REPO

echo "Triggering ad-hoc snapshot"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
curl -s -u "$ES_USER:$ES_PASS" --cacert "$CACERT" -X PUT "$ES_URL/_snapshot/$SNAPSHOT_REPO/security-backup-$TIMESTAMP" -H 'Content-Type: application/json' -d @- <<SNAP
{
  "indices": "security-scans-*",
  "ignore_unavailable": true,
  "include_global_state": false
}
SNAP

echo "Setup complete"
