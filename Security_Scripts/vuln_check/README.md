# vuln_check.py

## Purpose
Matches discovered service versions against a small, local database of CVEs. Use it to quickly identify known vulnerabilities in scan output from tools like `shodan-scanner.py`.

## Features
- Accepts JSON scan results containing service names and versions
- Looks up each service/version pair in an easily extendable CVE dictionary
- Outputs a list of vulnerable services with their matching CVE IDs
- Supports saving results to a JSON file or printing to the console

## Requirements
- Python 3.x

No external libraries are required beyond the Python standard library.

## Usage
```bash
python3 vuln_check.py -i shodan_results.json -o cve_matches.json
```

Arguments
- `-i, --input` – JSON file with service scan data (required)
- `-o, --output` – Optional JSON file to write matches

## Example Input
```json
{
  "198.51.100.23": {
    "data": [
      {"port": 80, "product": "Apache httpd", "version": "2.4.41"},
      {"port": 22, "product": "OpenSSH", "version": "7.4"}
    ]
  }
}
```

## Example Output
```json
[
  {
    "host": "198.51.100.23",
    "port": 80,
    "service": "Apache httpd",
    "version": "2.4.41",
    "cves": ["CVE-2021-41773", "CVE-2021-42013"]
  },
  {
    "host": "198.51.100.23",
    "port": 22,
    "service": "OpenSSH",
    "version": "7.4",
    "cves": ["CVE-2018-15473"]
  }
]
```

## Security Context
Running this script helps highlight services that may be exploitable based on known CVEs. Always use it only on networks and systems you are authorized to test.

## License
MIT License. Use at your own risk.
