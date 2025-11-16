# Security Scripts Toolkit

A collection of modular Python scripts for reconnaissance, vulnerability scanning, and security reporting.  
Built for educational purposes, portfolio demonstration, and authorized security assessments only.

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
| `port_scanner.py`       | Threaded TCP scanner with optional banner grabbing and top-port presets.   |
| `dns_enum.py`           | Enumerates DNS records and attempts AXFR zone transfers.                   |
| `who_geo.py`            | Performs Whois+RDAP lookups with ASN intelligence summaries.               |
| `cert_grabber.py`       | Fetches SSL/TLS metadata including SANs, cipher suites, and expiry.        |
| `meta_extract.py`       | Extracts metadata, hashes, and sensitive indicators from supplied files.   |
| `vuln_check.py`         | Maps open ports/services to curated KEV signatures with MITRE tagging.     |
| `exploit_checker.py`    | Matches services/versions against a CVE dataset with CVSS filtering.       |
| `email_head_tool.py`    | Analyzes SPF/DKIM/DMARC and reconstructs Received chains for anomalies.    |
| `password_spray.py`     | Adds throttling, multi-password rotation, and response heuristics.         |
| `markdown_gen.py`       | Generates Markdown/HTML reports from arbitrary JSON scan data.             |
| `csv_json_export.py`    | Exports scans with flattening, deduping, and field selection controls.     |
| `pentest_toolkit.py`    | Automates Metasploit RPC with configurable delays and JSON logging.        |
| `anomaly_detection.py`  | Enterprise IsolationForest pipeline with config-driven train/score/report. |
| `qrng_steganography/`   | CLI-driven LSB embedding/extraction (keyed + unkeyed) with HKDF hardening.  |

---

## Requirements

- Python 3.8+
- Python modules:
  ```bash
  pip install -r requirements.txt
  ```

### Additional External Tools
These are required by specific scripts:

- **hydra** — for `password_spray.py`
- **exiftool** — for `meta_extract.py`
- **nmap** (optional) — for local port scanning or verification

### Shodan API Key
Set your Shodan API key as an environment variable:
```bash
export SHODAN_API_KEY=<your_shodan_api_key>
```

## Setup

Clone the repository:
```bash
git clone https://github.com/artilleryjoe/Cybersecurity-Portfolio.git
cd Cybersecurity-Portfolio/Security_Scripts
```

Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # For Termux/Linux
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Tested Environments

- Ubuntu 22.04 LTS
  
- Termux (Pixel 9a)
  
- Local and virtual test lab networks

## Disclaimer

- Use these tools only on systems you own or have explicit written permission to test.
  
- Unauthorized use is illegal and unethical.
  
- This toolkit is intended for learning, research, and authorized security assessment only.

## Folder Structure

```
security-scripts-toolkit/
├── advanced-pentest-toolkit/
│   └── pentest_toolkit.py
├── cert_grabber.py
├── csv_json_export.py
├── dns_enum.py
├── email_head_tool.py
├── exploit_checker.py
├── markdown_gen.py
├── meta_extract.py
├── password_spray.py
├── port_scanner.py
├── requirements.txt
├── shodan-scanner.py
├── vuln_check.py
├── who_geo.py
└── README.md
```

## Author

Kristopher McCoy  
Cybersecurity Professional | Portfolio Project — July 2025  
GitHub: [github.com/artilleryjoe](https://github.com/artilleryjoe)
