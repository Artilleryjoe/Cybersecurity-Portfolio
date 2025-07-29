#!/usr/bin/env python3

import argparse
import email
import email.policy
from email.header import decode_header
import re
import sys

def parse_email_headers(raw_email_file):
    with open(raw_email_file, 'r') as f:
        raw_email = f.read()

    msg = email.message_from_string(raw_email, policy=email.policy.default)

    headers = {}
    for key, value in msg.items():
        # Decode headers that might be encoded (e.g. encoded-words)
        decoded_fragments = decode_header(value)
        decoded_string = ''
        for fragment, encoding in decoded_fragments:
            if isinstance(fragment, bytes):
                decoded_string += fragment.decode(encoding or 'utf-8', errors='replace')
            else:
                decoded_string += fragment
        headers[key] = decoded_string

    return headers

def analyze_spf(headers):
    # SPF results are often in Authentication-Results or Received-SPF headers
    auth_results = headers.get('Authentication-Results', '')
    spf_result = 'Not found'

    spf_match = re.search(r'spf=(pass|fail|neutral|softfail|none)', auth_results, re.IGNORECASE)
    if spf_match:
        spf_result = spf_match.group(1).lower()

    return spf_result

def analyze_dkim(headers):
    auth_results = headers.get('Authentication-Results', '')
    dkim_result = 'Not found'

    dkim_match = re.search(r'dkim=(pass|fail|neutral|none)', auth_results, re.IGNORECASE)
    if dkim_match:
        dkim_result = dkim_match.group(1).lower()

    return dkim_result

def analyze_dmarc(headers):
    auth_results = headers.get('Authentication-Results', '')
    dmarc_result = 'Not found'

    dmarc_match = re.search(r'dmarc=(pass|fail|policy)', auth_results, re.IGNORECASE)
    if dmarc_match:
        dmarc_result = dmarc_match.group(1).lower()

    return dmarc_result

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

    print(f"SPF result: {spf_result}")
    print(f"DKIM result: {dkim_result}")
    print(f"DMARC result: {dmarc_result}\n")

    print("## Key Headers:")
    for key in ["From", "To", "Subject", "Date", "Message-ID", "Received"]:
        value = headers.get(key)
        if value:
            print(f"{key}: {value}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
