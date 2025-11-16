#!/usr/bin/env python3

import argparse
import email
import email.policy
import email.utils
import re
import sys
from collections import defaultdict
from datetime import datetime
from email.header import decode_header
from typing import Dict, List


def _decode_value(value: str) -> str:
    decoded_fragments = decode_header(value)
    decoded_string = ''
    for fragment, encoding in decoded_fragments:
        if isinstance(fragment, bytes):
            decoded_string += fragment.decode(encoding or 'utf-8', errors='replace')
        else:
            decoded_string += fragment
    return decoded_string


def parse_email_headers(raw_email_file) -> Dict[str, List[str]]:
    with open(raw_email_file, 'r', encoding='utf-8', errors='ignore') as f:
        raw_email = f.read()

    msg = email.message_from_string(raw_email, policy=email.policy.default)

    headers: Dict[str, List[str]] = defaultdict(list)
    for key in msg.keys():
        for value in msg.get_all(key, []):
            headers[key].append(_decode_value(value))

    return headers

def analyze_spf(headers):
    # SPF results are often in Authentication-Results or Received-SPF headers
    auth_results = ' '.join(headers.get('Authentication-Results', []))
    spf_result = 'Not found'

    spf_match = re.search(r'spf=(pass|fail|neutral|softfail|none)', auth_results, re.IGNORECASE)
    if spf_match:
        spf_result = spf_match.group(1).lower()

    return spf_result

def analyze_dkim(headers):
    auth_results = ' '.join(headers.get('Authentication-Results', []))
    dkim_result = 'Not found'

    dkim_match = re.search(r'dkim=(pass|fail|neutral|none)', auth_results, re.IGNORECASE)
    if dkim_match:
        dkim_result = dkim_match.group(1).lower()

    return dkim_result

def analyze_dmarc(headers):
    auth_results = ' '.join(headers.get('Authentication-Results', []))
    dmarc_result = 'Not found'

    dmarc_match = re.search(r'dmarc=(pass|fail|policy)', auth_results, re.IGNORECASE)
    if dmarc_match:
        dmarc_result = dmarc_match.group(1).lower()

    return dmarc_result

def analyze_received(headers: Dict[str, List[str]]) -> List[dict]:
    chain = headers.get('Received', [])
    timeline: List[dict] = []
    for index, entry in enumerate(chain, 1):
        date_match = re.search(r';\s*(.+)$', entry)
        dt: datetime | None = None
        if date_match:
            try:
                dt = email.utils.parsedate_to_datetime(date_match.group(1))
            except Exception:
                dt = None
        ip_match = re.search(r'\[([0-9a-fA-F:.]+)\]', entry)
        timeline.append(
            {
                'hop': index,
                'timestamp': dt.isoformat() if dt else 'unknown',
                'raw': entry.strip(),
                'ip': ip_match.group(1) if ip_match else 'unknown',
            }
        )
    return timeline


def detect_spoofing(headers: Dict[str, List[str]]) -> str:
    from_header = headers.get('From', ['unknown'])[0]
    domain_match = re.search(r'@([^>]+)>?', from_header)
    domain = domain_match.group(1) if domain_match else None
    spf = analyze_spf(headers)
    if domain and spf not in {'pass', 'not found'}:
        return f"From domain {domain} failed SPF ({spf})"
    return 'No obvious spoofing indicators'


def main():
    parser = argparse.ArgumentParser(description="Email header analysis tool for SPF, DKIM, DMARC, and common header fields.")
    parser.add_argument('-i', '--input', required=True, help="Raw email file (.eml) to analyze")
    args = parser.parse_args()

    try:
        headers = parse_email_headers(args.input)
    except FileNotFoundError:
        print(f"[-] File not found: {args.input}")
        sys.exit(1)

    spf_result = analyze_spf(headers)
    dkim_result = analyze_dkim(headers)
    dmarc_result = analyze_dmarc(headers)
    timeline = analyze_received(headers)
    spoofing = detect_spoofing(headers)

    print(f"SPF result  : {spf_result}")
    print(f"DKIM result : {dkim_result}")
    print(f"DMARC result: {dmarc_result}")
    print(f"Spoofing    : {spoofing}\n")

    print("## Key Headers:")
    for key in ["From", "To", "Subject", "Date", "Message-ID"]:
        value = headers.get(key)
        if value:
            print(f"{key}: {value[0]}")

    if timeline:
        print("\n## Received Chain (top -> bottom):")
        for hop in timeline:
            print(f"Hop {hop['hop']:02d} | {hop['timestamp']} | {hop['ip']}")
            print(f"    {hop['raw']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
