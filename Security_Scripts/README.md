# Security Scripts Toolkit

A collection of modular Python scripts for reconnaissance, vulnerability scanning, and security reporting. Built for educational purposes, portfolio demonstration, and authorized security assessments only.

---

## Overview

This toolkit serves as a practical foundation for:

- Cybersecurity learners  
- Ethical hackers  
- Professionals conducting internal or authorized security assessments  

Each script is designed to be modular, standalone, and easily extensible.

---

## Included Scripts

| Script Name             | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| `shodan-scanner.py`     | Uses Shodan API to scan hosts for exposed services and grab banners.       |
| `port_scanner.py`       | Custom TCP port scanner targeting specified IPs and port ranges.           |
| `dns_enum.py`           | Enumerates DNS records and attempts AXFR zone transfers.                   |
| `who_geo.py`            | Performs Whois lookups and GeoIP geolocation queries.                      |
| `cert_grabber.py`       | Fetches SSL/TLS certificate metadata (issuer, expiration, etc.).           |
| `meta_extract.py`       | Extracts metadata from files (images, PDFs, Word documents).               |
| `vuln_check.py`         | Matches open ports/services to known CVEs for vulnerability awareness.     |
| `exploit_checker.py`    | Checks for common misconfigurations (e.g., SMBv1, RDP exposure).           |
| `email_head_tool.py`    | Analyzes email headers for SPF, DKIM, DMARC, and relay path insight.       |
| `password_spray.py`     | Executes password spray attacks (test environments only) using Hydra.      |
| `markdown_html_gen.py`  | Generates formatted Markdown and HTML reports from scan output.            |
| `csv_json_export.py`    | Exports scan results to both `.csv` and `.json` formats.                   |

---

## Requirements

- Python 3.8+
- Python modules:
  ```bash
  pip install -r requirements.txt
Additional external tools:

hydra — for password_spray.py

exiftool — for meta_extract.py

nmap (optional) — for comparison or local scans

Shodan API Key
Set your API key for shodan-scanner.py in your environment:

bash
  Copy
  Edit
  export SHODAN_API_KEY=your_api_key_here
  Setup
  Clone the repo:

bash
  Copy
  Edit
  git clone https://github.com/your-username/security-scripts-toolkit.git
  cd security-scripts-toolkit
  Create and activate a virtual environment:

bash
  Copy
  Edit
  python3 -m venv venv
  source venv/bin/activate   # Termux/Linux
  Install required modules:

bash
  Copy
  Edit
  pip install -r requirements.txt
  Tested Environments
  Ubuntu 22.04 LTS

Termux (Pixel 9a)

Local and virtual test lab networks

Disclaimer
Use these tools only on systems you own or have explicit written permission to test.
Unauthorized use is illegal and unethical.
This toolkit is intended for learning, research, and authorized security assessment only.


Author
Kristopher McCoy
Cybersecurity Professional | Portfolio Project — July 2025
GitHub: github.com/artilleryjoe
