#!/usr/bin/env bash
# Simple operational health check for IDS sensors
set -euo pipefail

SENSOR_NAME=${1:-$(hostname)}
LOG_DIR=${2:-/var/log/suricata}
THRESHOLD_DROP=${THRESHOLD_DROP:-1}
THRESHOLD_CPU=${THRESHOLD_CPU:-85}

if [[ ! -d "$LOG_DIR" ]]; then
  echo "[ERROR] Log directory $LOG_DIR not found" >&2
  exit 2
fi

STATS_FILE="$LOG_DIR/suricata.stats"
if [[ ! -f "$STATS_FILE" ]]; then
  echo "[WARN] Stats file $STATS_FILE not present yet"
else
  DROP=$(grep -E 'capture.kernel_drops' "$STATS_FILE" | tail -1 | awk '{print $2}')
  if [[ -n "$DROP" && "$DROP" -gt "$THRESHOLD_DROP" ]]; then
    echo "[ALERT] $SENSOR_NAME dropping packets: $DROP packets" >&2
  else
    echo "[OK] $SENSOR_NAME packet drops under threshold"
  fi
fi

CPU=$(top -bn1 | awk '/Suricata/{cpu+=$9} END {print cpu+0}')
if (( ${CPU%.*} > THRESHOLD_CPU )); then
  echo "[ALERT] $SENSOR_NAME CPU usage high: $CPU%" >&2
else
  echo "[OK] $SENSOR_NAME CPU usage $CPU%"
fi

systemctl is-active --quiet suricata && echo "[OK] Service suricata active" || {
  echo "[ALERT] Suricata service inactive" >&2
  exit 3
}
