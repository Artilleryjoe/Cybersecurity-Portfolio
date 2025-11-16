#!/usr/bin/env python3

import argparse
import json
import socket
import ssl
from datetime import datetime, timezone
from typing import Any, Dict


DATE_FORMAT = "%b %d %H:%M:%S %Y %Z"


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in (DATE_FORMAT, "%b %d %H:%M:%S %Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def get_certificate_info(host: str, port: int, timeout: float) -> Dict[str, Any]:
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host)
    conn.settimeout(timeout)

    try:
        conn.connect((host, port))
        cert = conn.getpeercert()
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

    info: Dict[str, Any] = {
        "subject": dict(x[0] for x in cert.get("subject", [])),
        "issuer": dict(x[0] for x in cert.get("issuer", [])),
        "serial_number": cert.get("serialNumber"),
        "not_before": cert.get("notBefore"),
        "not_after": cert.get("notAfter"),
        "version": cert.get("version"),
        "subject_alt_names": sorted({value for _, value in cert.get("subjectAltName", [])}),
        "ocsp": cert.get("OCSP"),
        "crl_distribution_points": cert.get("crlDistributionPoints"),
        "tls_version": conn.version(),
        "cipher": conn.cipher(),
    }

    not_before_dt = _parse_date(info["not_before"])
    not_after_dt = _parse_date(info["not_after"])
    if not_before_dt:
        info["not_before"] = not_before_dt.replace(tzinfo=timezone.utc).isoformat()
    if not_after_dt:
        info["not_after"] = not_after_dt.replace(tzinfo=timezone.utc).isoformat()
        info["expires_in_days"] = (not_after_dt - datetime.utcnow()).days

    return info


def print_certificate_summary(info: Dict[str, Any]) -> None:
    subject = info.get("subject", {})
    issuer = info.get("issuer", {})
    cn = subject.get("commonName") or subject.get("CN")
    issuer_cn = issuer.get("commonName") or issuer.get("CN")
    print("=== Certificate Summary ===")
    print(f"Subject CN : {cn or 'N/A'}")
    print(f"Issuer CN  : {issuer_cn or 'N/A'}")
    print(f"Serial     : {info.get('serial_number')}")
    print(f"Valid From : {info.get('not_before')}")
    print(f"Valid Until: {info.get('not_after')} ({info.get('expires_in_days', '??')} days remaining)")
    print(f"TLS Version: {info.get('tls_version')} | Cipher: {info.get('cipher')}")
    alts = info.get("subject_alt_names") or []
    if alts:
        preview = ", ".join(alts[:5])
        more = f" (+{len(alts)-5} more)" if len(alts) > 5 else ""
        print(f"SANs       : {preview}{more}")


def main():
    parser = argparse.ArgumentParser(description="Fetch SSL/TLS certificate info from a host.")
    parser.add_argument("-t", "--target", required=True, help="Target host (e.g., example.com)")
    parser.add_argument("-p", "--port", type=int, default=443, help="Port to connect to (default: 443)")
    parser.add_argument("-o", "--output", default="cert_info.json", help="Output JSON file")
    parser.add_argument("--timeout", type=float, default=5.0, help="Socket timeout in seconds")

    args = parser.parse_args()

    cert_info = get_certificate_info(args.target, args.port, args.timeout)

    with open(args.output, "w") as f:
        json.dump(cert_info, f, indent=2)

    print(f"[+] Certificate info saved to {args.output}")
    if "error" not in cert_info:
        print_certificate_summary(cert_info)


if __name__ == "__main__":
    main()
