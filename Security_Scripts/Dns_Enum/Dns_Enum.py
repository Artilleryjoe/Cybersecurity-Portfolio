#!/usr/bin/env python3
"""
dns_enum.py
Enumerates DNS records and attempts AXFR zone transfers for a target domain.
"""

import dns.resolver
import dns.query
import dns.zone
import argparse
import json

def query_dns_records(domain):
    """Query common DNS record types for the domain."""
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    results = {}

    resolver = dns.resolver.Resolver()
    for rtype in record_types:
        try:
            answers = resolver.resolve(domain, rtype)
            results[rtype] = [rdata.to_text() for rdata in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
            results[rtype] = []
    return results

def attempt_axfr(domain):
    """Attempt a DNS zone transfer (AXFR) for the domain."""
    axfr_results = {}
    resolver = dns.resolver.Resolver()

    try:
        ns_records = resolver.resolve(domain, 'NS')
    except Exception as e:
        print(f"[-] Failed to get NS records: {e}")
        return axfr_results

    for ns in ns_records:
        ns = ns.to_text()
        try:
            zone = dns.zone.from_xfr(dns.query.xfr(ns, domain, timeout=5))
            if zone:
                axfr_results[ns] = []
                for name, node in zone.nodes.items():
                    rdatasets = node.rdatasets
                    for rdataset in rdatasets:
                        for rdata in rdataset:
                            axfr_results[ns].append(f"{name} {rdataset.ttl} {rdataset.rdtype} {rdata.to_text()}")
        except Exception as e:
            axfr_results[ns] = f"Zone transfer failed: {e}"
    return axfr_results

def main():
    parser = argparse.ArgumentParser(description="DNS Enumerator and AXFR zone transfer tool")
    parser.add_argument("-d", "--domain", required=True, help="Target domain to enumerate")
    parser.add_argument("-o", "--output", default="dns_enum_results.json", help="Output JSON file")

    args = parser.parse_args()
    domain = args.domain

    print(f"[+] Querying DNS records for {domain}...")
    dns_records = query_dns_records(domain)

    print(f"[+] Attempting AXFR zone transfer for {domain}...")
    axfr_results = attempt_axfr(domain)

    output = {
        "domain": domain,
        "dns_records": dns_records,
        "axfr_zone_transfers": axfr_results
    }

    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)

    print(f"[+] Enumeration complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()

