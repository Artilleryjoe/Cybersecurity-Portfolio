# dns_enum.py

## Purpose

A DNS enumeration tool that queries common DNS records and attempts AXFR zone transfers for a given domain. Useful for reconnaissance and gathering DNS infrastructure information.

## Features

- Queries DNS records: A, AAAA, MX, NS, TXT, CNAME, SOA.
- Attempts DNS zone transfer (AXFR) on each nameserver.
- Detects wildcard DNS behavior and reports DNSSEC material availability.
- Optional subdomain brute forcing from a newline-delimited wordlist.
- Configurable resolver timeout, custom nameservers, and rate limiting to avoid noisy scans.
- Outputs structured JSON to disk and optionally echoes it to stdout for piping.

## Requirements

- Python 3.x
- `dnspython` library

## Installation

Install the required Python package:
  ```pip install dnspython```

## Usage

```bash
python3 dns_enum.py \
  --domain example.com \
  --output dns_results.json \
  --subdomains wordlist.txt \
  --nameserver 1.1.1.1 --nameserver 8.8.8.8 \
  --timeout 5 --rate-limit 0.25 --print
```

## Arguments:
-d, --domain: Target domain to enumerate (required).

-o, --output: Output JSON file path (default: dns_enum_results.json).

--subdomains: Optional newline-delimited wordlist used for passive brute forcing.

--nameserver: Override the resolver's nameserver list. Repeatable.

--timeout: DNS resolver timeout (seconds).

--rate-limit: Seconds to sleep between individual queries to reduce traffic bursts.

--print: Also echo the JSON output to stdout.

## Example Output (dns_results.json)
```json
  {
    "domain": "example.com",
    "dns_records": {
      "A": ["93.184.216.34"],
      "AAAA": [],
      "MX": ["0 mail.example.com."],
      "NS": ["ns1.example.com.", "ns2.example.com."],
      "TXT": ["v=spf1 include:_spf.example.com ~all"],
      "CNAME": [],
      "SOA": ["ns1.example.com. hostmaster.example.com. 2021071501 7200 3600 1209600 3600"]
    },
    "axfr_zone_transfers": {
      "ns1.example.com.": "Zone transfer failed: timed out",
      "ns2.example.com.": "Zone transfer failed: timed out"
    }
  }
```
## Security Context
Only run this script against domains you own or have explicit permission to test. Unauthorized zone transfers or enumeration may be illegal.

## Notes
Zone transfers are often disabled; failures are normal.

The script handles exceptions and timeouts gracefully.

## License
MIT License

  
