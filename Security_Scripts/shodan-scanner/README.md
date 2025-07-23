Usage Instructions
Run the script with:

bash

Collapse

Wrap

Run

Copy
python3 shodan-scanner.py -k YOUR_API_KEY -i targets.txt -o results.json
-k: Your Shodan API key (required).
-i: Path to a text file with one IP address per line (required).
-o: Output JSON file path (optional, defaults to shodan_output.json).
Example Input (targets.txt)
text

Collapse

Wrap

Copy
198.51.100.23
203.0.113.17
192.0.2.88
Example Output (results.json)
json

Collapse

Wrap

Copy
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
Security Notes
Purpose: Identifies misconfigured services, exposed ports, and known vulnerabilities for external assessments.
Caution: Only scan infrastructure you own or have explicit permission to test to avoid legal issues.
Rate Limits: The script includes a 1-second delay between API calls to respect Shodan’s free API tier limits.
Integrations
vuln_check.py: Use to further analyze CVEs from the output.
markdown_html_gen.py: Convert the JSON output into styled markdown or HTML reports for presentations.
This script is production-ready and designed for integration into reporting pipelines. Let me know if you need help with the integrations or further customization!
