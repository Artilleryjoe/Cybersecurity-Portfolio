#!/usr/bin/env python3
"""
port_scanner.py
Custom TCP port scanner to check specified IP addresses and port ranges for open ports.
"""

import socket
import argparse
import threading
import json
from queue import Queue

# Thread worker function to scan ports
def scan_port(ip, port, results):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            # Port is open
            results.append(port)
        sock.close()
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(description="Custom TCP port scanner.")
    parser.add_argument("-t", "--target", required=True, help="Target IP address to scan")
    parser.add_argument("-p", "--ports", required=True, help="Port range to scan, e.g. 1-1024")
    parser.add_argument("-o", "--output", default="port_scan_results.json", help="Output JSON file")

    args = parser.parse_args()

    target_ip = args.target
    port_range = args.ports

    # Parse ports
    if "-" in port_range:
        start_port, end_port = map(int, port_range.split("-"))
    else:
        start_port = end_port = int(port_range)

    ports_to_scan = range(start_port, end_port + 1)
    open_ports = []

    threads = []
    results = []

    for port in ports_to_scan:
        t = threading.Thread(target=scan_port, args=(target_ip, port, results))
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()

    # Prepare output with mock service names (simple mapping)
    common_services = {
        22: "SSH",
        80: "HTTP",
        443: "HTTPS",
        3389: "RDP",
        3306: "MySQL",
        53: "DNS"
    }

    output_data = {
        "host": target_ip,
        "open_ports": [
            {"port": port, "service": common_services.get(port, "Unknown")} for port in sorted(results)
        ]
    }

    # Write output to JSON file
    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"[+] Scan complete. Open ports saved to {args.output}")

if __name__ == "__main__":
    main()
