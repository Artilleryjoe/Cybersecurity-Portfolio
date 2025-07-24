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

## Example Output (dns_results.json)
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

## Security Context
Only run this script against domains you own or have explicit permission to test. Unauthorized zone transfers or enumeration may be illegal.

## Notes
Zone transfers are often disabled; failures are normal.

The script handles exceptions and timeouts gracefully.

## License
MIT License

  
