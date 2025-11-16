#!/usr/bin/env python3
"""
dns_enum.py
Enumerates DNS records and attempts AXFR zone transfers for a target domain.
"""

import argparse
import json
import secrets
from pathlib import Path

import dns.query
import dns.resolver
import dns.zone

def query_dns_records(domain, resolver: dns.resolver.Resolver | None = None):
    """Query common DNS record types for the domain."""
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    results = {}

    resolver = resolver or dns.resolver.Resolver()
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


def detect_wildcard(domain: str, resolver: dns.resolver.Resolver) -> bool:
    probe = f"{secrets.token_hex(8)}.{domain}"
    try:
        resolver.resolve(probe, 'A')
        return True
    except Exception:
        return False


def check_dnssec(domain: str, resolver: dns.resolver.Resolver) -> dict:
    status = {"dnskey": False, "ds": False}
    try:
        answers = resolver.resolve(domain, 'DNSKEY')
        status["dnskey"] = len(answers) > 0
    except Exception:
        pass
    try:
        answers = resolver.resolve(domain, 'DS')
        status["ds"] = len(answers) > 0
    except Exception:
        pass
    status["dnssec_enabled"] = status["dnskey"] and status["ds"]
    return status


def brute_force_subdomains(domain: str, wordlist: Path, resolver: dns.resolver.Resolver) -> dict:
    findings: dict[str, dict[str, list[str]]] = {}
    if not wordlist.exists():
        return findings
    for word in wordlist.read_text(encoding='utf-8').splitlines():
        word = word.strip()
        if not word:
            continue
        hostname = f"{word}.{domain}"
        findings[hostname] = {}
        for record in ('A', 'AAAA'):
            try:
                answers = resolver.resolve(hostname, record)
                findings[hostname][record] = [rdata.to_text() for rdata in answers]
            except Exception:
                findings[hostname][record] = []
        if not any(findings[hostname].values()):
            findings.pop(hostname, None)
    return findings

def main():
    parser = argparse.ArgumentParser(description="DNS Enumerator and AXFR zone transfer tool")
    parser.add_argument("-d", "--domain", required=True, help="Target domain to enumerate")
    parser.add_argument("-o", "--output", default="dns_enum_results.json", help="Output JSON file")
    parser.add_argument(
        "--subdomains",
        type=Path,
        help="Optional newline-delimited wordlist for passive subdomain brute forcing",
    )

    args = parser.parse_args()
    domain = args.domain

    resolver = dns.resolver.Resolver()

    print(f"[+] Querying DNS records for {domain}...")
    dns_records = query_dns_records(domain, resolver)

    print(f"[+] Attempting AXFR zone transfer for {domain}...")
    axfr_results = attempt_axfr(domain)

    dnssec = check_dnssec(domain, resolver)
    wildcard = detect_wildcard(domain, resolver)
    bruteforce = brute_force_subdomains(domain, args.subdomains, resolver) if args.subdomains else {}

    output = {
        "domain": domain,
        "dns_records": dns_records,
        "axfr_zone_transfers": axfr_results,
        "dnssec": dnssec,
        "wildcard": wildcard,
        "subdomains": bruteforce,
    }

    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)

    print(f"[+] Enumeration complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()

