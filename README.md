# Security Scripts Toolkit

A collection of modular Python scripts for reconnaissance, vulnerability scanning, and reporting. Built for educational purposes, portfolio demonstration, and authorized security assessments.

# Security Scripts Portfolio

A collection of custom security and reconnaissance scripts developed as part of a hands-on cybersecurity project portfolio. These scripts cover various aspects of network and system security analysis, including vulnerability scanning, DNS enumeration, certificate grabbing, metadata extraction, exploit checks, email header analysis, password spraying (test environments only), and report generation.

---

## Overview

This toolkit serves as a practical foundation for security assessments and learning, focusing on real-world tools and API integrations. It is designed to be modular and extensible for ongoing development and professional use.

---

## Included Scripts

| Script Name               | Description                                             |
|--------------------------|---------------------------------------------------------|
| **shodan-scanner.py**     | Uses Shodan API to scan hosts for exposed services and banners. |
| **port_scanner.py**       | Custom TCP port scanner for specified ports.            |
| **dns_enum.py**           | Enumerates DNS records and attempts zone transfers.     |
| **who_geo.py**            | Performs Whois and GeoIP lookups on IP addresses or domains. |
| **cert_grabber.py**       | Retrieves SSL/TLS certificate information and expiration. |
| **meta_extract.py**       | Extracts metadata from files (images, PDFs, DOCX).       |
| **vuln_check.py**         | Matches open ports and services to known CVEs.           |
| **exploit_checker.py**    | Checks for common exploits like SMBv1 and exposed RDP.   |
| **email_head_tool.py**    | Analyzes email headers for SPF, DKIM, DMARC, and relay paths. |
| **password_spray.py**     | Performs password spray attacks in test environments using Hydra. |
| **markdown_html_gen.py**  | Generates clean Markdown and HTML summary reports.       |
| **csv_json_export.py**    | Exports scan results and data in CSV and JSON formats.   |

---

## Requirements

- Python 3.8+
- Modules: `requests`, `dnspython`, `python-docx`, `PyPDF2`, `shodan` (install via `pip install -r requirements.txt`)
- External tools (for some scripts):
  - `exiftool`
  - `hydra`
  - `nmap` (optional, for comparison/testing)
- Valid Shodan API key stored in environment variable `SHODAN_API_KEY`

---

## Setup

1. Clone this repository.
2. Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate

Ubuntu 22.04 and Termux on Pixel 9a

Local virtual lab

Disclaimer
Use only on systems you own or have explicit permission to test. Unauthorized use is illegal and unethical.
