#!/usr/bin/env python3
"""
shodan-scanner.py
Uses the Shodan API to scan a list of IP addresses and retrieve service banners and vulnerability info.
Requires a valid Shodan API key.
"""

import shodan
import argparse
import json
import time
from typing import List

# Initialize argument parser
parser = argparse.ArgumentParser(description="Scan targets with Shodan API and retrieve exposed services.")
parser.add_argument("-k", "--apikey", required=True, help="Your Shodan API key")
parser.add_argument("-i", "--input", required=True, help="Path to file with list of target IPs")
parser.add_argument("-o", "--output", required=False, help="Output JSON file", default="shodan_output.json")

args = parser.parse_args()

# Initialize Shodan API
api = shodan.Shodan(args.apikey)

# Read target IPs
with open(args.input, "r") as f:
    targets = [line.strip() for line in f if line.strip()]

results = {}

for ip in targets:
    try:
        print(f"[+] Querying Shodan for {ip}...")
        host = api.host(ip)
        result = {
            "ip": host.get("ip_str"),
            "org": host.get("org", "N/A"),
            "os": host.get("os", "N/A"),
            "ports": host.get("ports", []),
            "data": [],
            "vulns": host.get("vulns", [])
        }

        for item in host.get("data", []):
            result["data"].append({
                "port": item.get("port"),
                "transport": item.get("transport"),
                "product": item.get("product"),
                "version": item.get("version"),
                "banner": item.get("data", "")[:100]  # Limit banner size
            })

        results[ip] = result
        time.sleep(1)  # Avoid hitting rate limits

    except shodan.APIError as e:
        print(f"[-] Error retrieving data for {ip}: {e}")
        results[ip] = {"error": str(e)}

# Save results
with open(args.output, "w") as out:
    json.dump(results, out, indent=2)

print(f"[+] Scan complete. Results saved to {args.output}")
