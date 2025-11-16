#!/usr/bin/env python3
"""Threaded TCP port scanner with optional banner grabbing."""

from __future__ import annotations

import argparse
import json
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, List

TOP_PORTS = [80, 443, 22, 21, 25, 110, 143, 3389, 8080, 8443, 5900, 445, 139, 53, 123]


def parse_ports(port_spec: str) -> Iterable[int]:
    port_spec = port_spec.strip()
    if port_spec.lower() == "top100":
        return TOP_PORTS
    if "-" in port_spec:
        start_port, end_port = map(int, port_spec.split("-"))
        if start_port > end_port:
            start_port, end_port = end_port, start_port
        return range(start_port, end_port + 1)
    if "," in port_spec:
        return [int(p) for p in port_spec.split(",")]
    return [int(port_spec)]


def identify_service(port: int) -> str:
    try:
        return socket.getservbyport(port)
    except OSError:
        return "Unknown"


def scan_port(ip: str, port: int, timeout: float, grab_banner: bool) -> dict | None:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        if result != 0:
            return None
        banner = None
        if grab_banner:
            try:
                sock.sendall(b"\r\n")
                data = sock.recv(1024)
                banner = data.decode(errors="ignore").strip()
            except Exception:
                banner = None
        return {
            "port": port,
            "service": identify_service(port),
            "banner": banner,
        }
    except Exception:
        return None
    finally:
        try:
            sock.close()
        except Exception:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Custom TCP port scanner.")
    parser.add_argument("-t", "--target", required=True, help="Target IP address to scan")
    parser.add_argument("-p", "--ports", required=True, help="Port range (e.g. 1-1024) or 'top100'")
    parser.add_argument("-o", "--output", default="port_scan_results.json", help="Output JSON file")
    parser.add_argument("--timeout", type=float, default=1.0, help="Socket timeout in seconds")
    parser.add_argument("--workers", type=int, default=100, help="Number of concurrent workers")
    parser.add_argument("--banner", action="store_true", help="Attempt lightweight banner grabbing")

    args = parser.parse_args()

    ports_to_scan = list(parse_ports(args.ports))
    results: List[dict] = []

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_port = {
            executor.submit(scan_port, args.target, port, args.timeout, args.banner): port
            for port in ports_to_scan
        }
        for future in as_completed(future_to_port):
            finding = future.result()
            if finding:
                results.append(finding)

    output_data = {
        "host": args.target,
        "scanned_ports": len(ports_to_scan),
        "open_ports": sorted(results, key=lambda item: item["port"]),
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"[+] Scan complete. Open ports saved to {args.output}")


if __name__ == "__main__":
    main()
