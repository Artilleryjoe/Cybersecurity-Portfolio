#!/usr/bin/env python3
"""
who_geo.py

Performs a Whois lookup and GeoIP geolocation query for a given domain or IP.
Outputs results in structured JSON format.
"""

import argparse
import ipaddress
import json
import socket

from ipwhois import IPWhois
import whois

def resolve_domain(target):
    try:
        ipaddress.ip_address(target)
        return target
    except ValueError:
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
            "cidr": res.get("network", {}).get("cidr"),
            "abuse_contacts": res.get("objects", {}).get(res.get("asn", ""), {}).get("contact", {}),
            "reverse_dns": reverse_dns(ip),
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


def reverse_dns(ip: str) -> str | None:
    try:
        host, *_ = socket.gethostbyaddr(ip)
        return host
    except Exception:
        return None


def print_summary(info: dict) -> None:
    whois_data = info.get("whois", {})
    geo = info.get("geoip", {})
    if "error" in whois_data:
        print(f"Whois: {whois_data['error']}")
    else:
        print(f"Registrar: {whois_data.get('registrar')}")
        print(f"Created : {whois_data.get('creation_date')} | Expires: {whois_data.get('expiration_date')}")
    if "error" in geo:
        print(f"GeoIP: {geo['error']}")
    else:
        print(f"ASN: {geo.get('asn')} ({geo.get('asn_description')})")
        print(f"Network: {geo.get('cidr')} in {geo.get('country')} via {geo.get('registry')}")
        reverse = geo.get('reverse_dns')
        if reverse:
            print(f"Reverse DNS: {reverse}")

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
    print_summary(result)

if __name__ == "__main__":
    main()

