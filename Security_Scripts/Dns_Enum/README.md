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

```bash
  pip install dnspython

