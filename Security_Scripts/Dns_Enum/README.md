# dns_enum.py

## Purpose

A DNS enumeration tool that queries common DNS records and attempts AXFR zone transfers for a given domain. Useful for reconnaissance and gathering DNS infrastructure information.

## Features

- Queries DNS records: A, AAAA, MX, NS, TXT, CNAME, SOA.
- Attempts DNS zone transfer (AXFR) on each nameserver.
- Outputs results in JSON format.

## Requirements

- Python 3.x
- `dnspython` library

## Installation

Install the required Python package:
  ```pip install dnspython```

## Usage
python3 dns_enum.py -d example.com -o dns_results.json

## Arguments:
-d, --domain: Target domain to enumerate (required).

-o, --output: Output JSON file path (default: dns_enum_results.json).

Example Output (dns_results.json)
