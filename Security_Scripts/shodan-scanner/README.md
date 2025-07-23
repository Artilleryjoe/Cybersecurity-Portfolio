# Script: `shodan-scanner.py`

## Purpose
Queries the Shodan API to retrieve information about IP addresses, including open ports, service banners, and known vulnerabilities.

---

##  Features

- Accepts a list of IPs via a text file.
- Uses Shodan API to retrieve metadata, banners, and CVEs.
- Saves structured output to JSON for later parsing.
- Built-in delay to respect Shodan rate limits.

---

## Technologies Used

- Python 3
- `shodan` library
- `argparse`, `json`, `time`

---

## Usage

```bash
python3 shodan-scanner.py -k YOUR_API_KEY -i targets.txt -o results.json
-k Your Shodan API key.

-i Text file with one IP per line.

-o (Optional) Output JSON file path (default: shodan_output.json)

Example Input: targets.txt
Copy
Edit
198.51.100.23
203.0.113.17
192.0.2.88
Example Output (Truncated):
json
Copy
Edit
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
Security Context
This script helps identify:

Misconfigured or exposed services

Known vulnerabilities based on banners and Shodan tags

Attack surface visibility for external assessments

Caution: Use only on infrastructure you own or have explicit permission to test.

Integrations
Use in combination with:

vuln_check.py for CVE matching

markdown_html_gen.py to convert this JSON output into a styled report

 Status
 Production-ready
 Rate-limited by Shodan’s free API tier
 Outputs ready for reporting pipelines
