# Custom Intrusion Detection System (IDS)

## Overview
A lightweight lab for experimenting with Snort or Suricata to detect threats using custom network rules.

## Prerequisites
- Snort or Suricata installed
- Network interface or pcap file for testing

## Setup
1. Install your preferred IDS (Snort or Suricata).
2. Copy the rule file from `rules/local.rules` into your IDS rules directory.
3. Start the IDS referencing the custom rule set.
4. Generate or replay traffic to trigger alerts and verify detection.

## Notes
- Tuning false positives and handling high-volume traffic require ongoing adjustment.
- Future enhancements include SIEM integration and pairing with anomaly detection.

## Resources
- [Snort Documentation](https://www.snort.org/documents)
