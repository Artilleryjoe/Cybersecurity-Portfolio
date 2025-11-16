#!/usr/bin/env python3
"""DNS enumeration helper with structured output and safety features."""
from __future__ import annotations

import argparse
import json
import secrets
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

import dns.exception
import dns.query
import dns.resolver
import dns.zone


RECORD_TYPES = ("A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA")


@dataclass
class EnumerationResult:
    """Serializable container for enumeration results."""

    domain: str
    dns_records: dict[str, list[str]]
    axfr_zone_transfers: dict[str, list[str] | str]
    dnssec: dict[str, bool]
    wildcard: bool
    subdomains: dict[str, dict[str, list[str]]]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class DnsEnumerator:
    """Stateful helper that shares resolver configuration across lookups."""

    def __init__(
        self,
        domain: str,
        resolver: dns.resolver.Resolver | None = None,
        *,
        rate_limit: float = 0.0,
    ) -> None:
        self.domain = domain
        self.resolver = resolver or dns.resolver.Resolver()
        self.rate_limit = max(rate_limit, 0.0)

    def query_dns_records(self, record_types: Iterable[str] = RECORD_TYPES) -> dict[str, list[str]]:
        """Return common DNS records for the configured domain."""

        results: dict[str, list[str]] = {}
        for record_type in record_types:
            results[record_type] = self._resolve_rdataset(self.domain, record_type)
        return results

    def attempt_zone_transfers(self, nameservers: Sequence[str]) -> dict[str, list[str] | str]:
        """Attempt AXFR transfers against discovered or configured nameservers."""

        axfr_results: dict[str, list[str] | str] = {}
        servers = [ns.strip() for ns in nameservers if ns.strip()]
        if not servers:
            servers = list(self.resolver.nameservers)
        for ns in servers:
            try:
                transfer = dns.query.xfr(ns, self.domain, timeout=self.resolver.timeout)
                zone = dns.zone.from_xfr(transfer)
            except Exception as exc:  # pragma: no cover - best effort network action
                axfr_results[ns] = f"Zone transfer failed: {exc}"
                continue
            if not zone:
                axfr_results[ns] = "Zone transfer returned no data"
                continue
            entries: list[str] = []
            for name, node in zone.nodes.items():
                for rdataset in node.rdatasets:
                    for rdata in rdataset:
                        entries.append(
                            f"{name} {rdataset.ttl} {dns.rdatatype.to_text(rdataset.rdtype)} {rdata.to_text()}"
                        )
            axfr_results[ns] = entries
        return axfr_results

    def detect_wildcard(self) -> bool:
        """Probe whether the domain resolves arbitrary hostnames."""

        probe = f"{secrets.token_hex(8)}.{self.domain}"
        return bool(self._resolve_rdataset(probe, "A"))

    def check_dnssec(self) -> dict[str, bool]:
        """Report DNSSEC material availability."""

        dnskey_records = self._resolve_rdataset(self.domain, "DNSKEY")
        ds_records = self._resolve_rdataset(self.domain, "DS")
        return {
            "dnskey": bool(dnskey_records),
            "ds": bool(ds_records),
            "dnssec_enabled": bool(dnskey_records and ds_records),
        }

    def brute_force_subdomains(self, wordlist: Path) -> dict[str, dict[str, list[str]]]:
        """Resolve hostnames from a wordlist and return any records."""

        findings: dict[str, dict[str, list[str]]] = {}
        if not wordlist.exists():
            return findings
        try:
            words = [
                line.strip()
                for line in wordlist.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.startswith("#")
            ]
        except OSError as exc:
            print(f"[-] Failed to read {wordlist}: {exc}", file=sys.stderr)
            return findings

        for word in words:
            hostname = f"{word}.{self.domain}"
            host_records: dict[str, list[str]] = {}
            for record in ("A", "AAAA"):
                answers = self._resolve_rdataset(hostname, record)
                if answers:
                    host_records[record] = answers
            if host_records:
                findings[hostname] = host_records
        return findings

    def enumerate(self, wordlist: Path | None = None) -> EnumerationResult:
        records = self.query_dns_records()
        dnssec = self.check_dnssec()
        wildcard = self.detect_wildcard()
        bruteforce = self.brute_force_subdomains(wordlist) if wordlist else {}
        axfr = self.attempt_zone_transfers(records.get("NS", []))
        return EnumerationResult(
            domain=self.domain,
            dns_records=records,
            axfr_zone_transfers=axfr,
            dnssec=dnssec,
            wildcard=wildcard,
            subdomains=bruteforce,
        )

    def _resolve_rdataset(self, name: str, record_type: str) -> list[str]:
        """Resolve a record type while honoring the rate limit."""

        if self.rate_limit:
            time.sleep(self.rate_limit)
        try:
            answers = self.resolver.resolve(name, record_type)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout, dns.resolver.NoNameservers):
            return []
        except dns.exception.DNSException as exc:
            print(f"[-] DNS error for {name} {record_type}: {exc}", file=sys.stderr)
            return []
        return [rdata.to_text() for rdata in answers]


def configure_resolver(nameservers: Sequence[str], timeout: float) -> dns.resolver.Resolver:
    resolver = dns.resolver.Resolver()
    cleaned = [ns.strip() for ns in nameservers if ns.strip()]
    if cleaned:
        resolver.nameservers = cleaned
    resolver.timeout = timeout
    resolver.lifetime = timeout
    return resolver


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DNS Enumerator with optional brute force and DNSSEC checks")
    parser.add_argument("-d", "--domain", required=True, help="Target domain to enumerate")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("dns_enum_results.json"),
        help="Output JSON file",
    )
    parser.add_argument(
        "--subdomains",
        type=Path,
        help="Optional newline-delimited wordlist for passive subdomain brute forcing",
    )
    parser.add_argument(
        "--nameserver",
        action="append",
        default=[],
        metavar="IP",
        help="Override resolver nameserver (repeatable)",
    )
    parser.add_argument("--timeout", type=float, default=3.0, help="DNS resolver timeout in seconds (default: 3.0)")
    parser.add_argument("--rate-limit", type=float, default=0.0, help="Seconds to sleep between DNS queries")
    parser.add_argument("--print", dest="print_stdout", action="store_true", help="Also print the JSON report to stdout")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    timeout = max(args.timeout, 0.5)
    resolver = configure_resolver(args.nameserver, timeout)
    enumerator = DnsEnumerator(args.domain, resolver=resolver, rate_limit=max(args.rate_limit, 0.0))
    wordlist = args.subdomains if args.subdomains else None
    result = enumerator.enumerate(wordlist)
    payload = result.to_dict()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[+] Enumeration complete. Results saved to {args.output}")
    if args.print_stdout:
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
