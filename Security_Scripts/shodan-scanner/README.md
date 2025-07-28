# shodan-scanner.py

## Purpose

This script queries the Shodan API to retrieve information about IP addresses, including open ports, service banners, and known vulnerabilities. It is useful during reconnaissance and exposure assessments.

## Features

- Accepts a list of IP addresses from a text file.
- Retrieves metadata including:
  - Organization
  - OS (if known)
  - Open ports
  - Service banners
  - Known vulnerabilities (CVEs)
- Outputs a structured JSON report.

## Requirements

- Python 3.x
- `shodan` Python library
- Valid Shodan API key

## Installation

Install the required Python package:

pip install shodan

shell
Copy
Edit

## Usage

```python3 shodan-scanner.py -k YOUR_API_KEY -i targets.txt -o results.json

Arguments:

- `-k`, `--apikey` - Your Shodan API key (required)
- `-i`, `--input` - Path to a file containing IP addresses, one per line (required)
- `-o`, `--output` - Output file for results in JSON format (default: `shodan_output.json`)

## Example Input: targets.txt

198.51.100.23
203.0.113.17
192.0.2.88

bash
Copy
Edit

## Example Output (truncated)

```json
{
  "198.51.100.23": {
    "ip": "198.51.100.23",
    "org": "Example ISP",
    "os": "Linux",
    "ports": [22, 80, 443],
    "data": [
      {
        "port": 80,
        "transport": "tcp",
        "product": "Apache httpd",
        "version": "2.4.41",
        "banner": "HTTP/1.1 200 OK ..."
      }
    ],
    "vulns": ["CVE-2021-41773", "CVE-2020-11984"]
  }
}
```
## Security Context
This script helps identify publicly exposed services and known vulnerabilities associated with those services. It should only be used on networks and systems you own or have explicit authorization to test.

## Integration
The output of this script can be further analyzed using:

vuln_check.py - For matching services against CVE databases

markdown_html_gen.py - To convert results into readable reports

csv_json_export.py - To reformat the data for different pipelines

## License
MIT License. Use at your own risk.
