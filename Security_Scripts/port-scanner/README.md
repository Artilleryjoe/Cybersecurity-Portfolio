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
Arguments:
-t, --target: Target IP address to scan (required).

-p, --ports: Port or port range to scan, e.g., 22 or 1-1024 (required).

-o, --output: Output JSON file path (default: port_scan_results.json).

Example Output (scan_results.json)
json
Copy
Edit
{
  "host": "192.0.2.5",
  "open_ports": [
    { "port": 22, "service": "SSH" },
    { "port": 80, "service": "HTTP" },
    { "port": 443, "service": "HTTPS" }
  ]
}```bash
python3 port_scanner.py -t 192.0.2.5 -p 1-1024 -o scan_results.json
Arguments:

-t, --target: Target IP address to scan (required).

-p, --ports: Port or port range to scan, e.g., 22 or 1-1024 (required).

-o, --output: Output JSON file path (default: port_scan_results.json).

Example Output (scan_results.json)
json
  {
    "host": "192.0.2.5",
    "open_ports": [
      { "port": 22, "service": "SSH" },
      { "port": 80, "service": "HTTP" },
      { "port": 443, "service": "HTTPS" }
    ]
  }

Security Context
This script is intended for use on authorized networks only. Port scanning unauthorized systems can be illegal and unethical.

Notes
The service names for ports are basic common mappings and may not reflect actual services.

Timeout and threading are configured for a balance between speed and accuracy.

License
MIT License
