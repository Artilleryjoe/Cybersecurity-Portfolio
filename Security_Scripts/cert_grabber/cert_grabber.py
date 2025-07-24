#!/usr/bin/env python3

import argparse
import ssl
import socket
import json
from datetime import datetime


def get_certificate_info(host, port):
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host)
    conn.settimeout(5.0)

    try:
        conn.connect((host, port))
        cert = conn.getpeercert()
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

    info = {
        "subject": dict(x[0] for x in cert.get("subject", [])),
        "issuer": dict(x[0] for x in cert.get("issuer", [])),
        "serial_number": cert.get("serialNumber"),
        "not_before": cert.get("notBefore"),
        "not_after": cert.get("notAfter"),
        "version": cert.get("version"),
    }

    # Convert dates to ISO 8601
    try:
        info["not_before"] = datetime.strptime(info["not_before"], "%b %d %H:%M:%S %Y %Z").isoformat()
        info["not_after"] = datetime.strptime(info["not_after"], "%b %d %H:%M:%S %Y %Z").isoformat()
    except Exception:
        pass  # leave original if parsing fails

    return info


def main():
    parser = argparse.ArgumentParser(description="Fetch SSL/TLS certificate info from a host.")
    parser.add_argument("-t", "--target", required=True, help="Target host (e.g., example.com)")
    parser.add_argument("-p", "--port", type=int, default=443, help="Port to connect to (default: 443)")
    parser.add_argument("-o", "--output", default="cert_info.json", help="Output JSON file")

    args = parser.parse_args()

    cert_info = get_certificate_info(args.target, args.port)

    with open(args.output, "w") as f:
        json.dump(cert_info, f, indent=2)

    print(f"[+] Certificate info saved to {args.output}")


if __name__ == "__main__":
    main()
