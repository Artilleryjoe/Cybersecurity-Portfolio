#!/usr/bin/env python3
"""
who_geo.py

Performs a Whois lookup and GeoIP geolocation query for a given domain or IP.
Outputs results in structured JSON format.
"""

import argparse
import json
import socket
from ipwhois import IPWhois
import whois

def resolve_domain(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return None

def get_geoip_info(ip):
    try:
        obj = IPWhois(ip)
        res = obj.lookup_rdap()
        return {
            "ip": ip,
            "asn": res.get("asn"),
            "asn_description": res.get("asn_description"),
            "country": res.get("network", {}).get("country"),
            "network_name": res.get("network", {}).get("name"),
            "registry": res.get("network", {}).get("rir"),
        }
    except Exception as e:
        return {"error": f"GeoIP lookup failed: {str(e)}"}

def get_whois_info(domain):
    try:
        w = whois.whois(domain)
        return {
            "domain": domain,
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": w.name_servers,
            "emails": w.emails
        }
    except Exception as e:
        return {"error": f"Whois lookup failed: {str(e)}"}

def main():
    parser = argparse.ArgumentParser(description="Perform Whois and GeoIP lookups.")
    parser.add_argument("-t", "--target", required=True, help="Target domain or IP address.")
    parser.add_argument("-o", "--output", default="who_geo_results.json", help="Output JSON file path.")
    args = parser.parse_args()

    result = {}

    ip = resolve_domain(args.target)
    result["whois"] = get_whois_info(args.target)
    if ip:
        result["geoip"] = get_geoip_info(ip)
    else:
        result["geoip"] = {"error": "Unable to resolve target to IP"}

    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    print(f"[+] Results saved to {args.output}")

if __name__ == "__main__":
    main()

