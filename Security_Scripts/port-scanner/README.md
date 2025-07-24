# port_scanner.py

## Purpose

A custom TCP port scanner script that scans specified IP addresses and port ranges for open TCP ports. Useful for network reconnaissance and verifying firewall or service configurations.

## Features

- Supports scanning single ports or port ranges (e.g., 1-1024).
- Uses multi-threading to speed up scanning.
- Outputs results in JSON format with port numbers and common service names.
- Simple and lightweight alternative to Nmap for basic scans.

## Requirements

- Python 3.x

## Usage

```bash
python3 port_scanner.py -t 192.0.2.5 -p 1-1024 -o scan_results.json
