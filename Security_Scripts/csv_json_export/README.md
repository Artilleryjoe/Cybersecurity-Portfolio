csv_json_export.py
Purpose
This script converts structured reconnaissance data (usually a list of dictionaries) into both .csv and .json formats. It’s designed to standardize output from tools in your recon pipeline for easier integration with reporting tools or external analysis.

Features
Accepts JSON input from file or standard input.

Supports exporting to:

JSON (pretty-printed)

CSV (from list-of-dict data)

Flexible file naming via output base name argument.

Requirements
Python 3.x

Installation
No external libraries required. Standard Python installation is sufficient.

Usage
bash
Copy
Edit
# Export both CSV and JSON from a file
python3 csv_json_export.py -i recon_results.json -f both -o exported_data

# Export only CSV, using stdin
cat recon_results.json | python3 csv_json_export.py -f csv
Arguments
-i, --input – Path to a JSON input file (optional if using stdin)

-o, --output – Base name for output file(s) (optional; default derived from input name or "output")

-f, --format – Export format: csv, json, or both (default: both)

Example Input (JSON)
```json
Copy
Edit
[
  {
    "ip": "192.168.1.1",
    "port": 80,
    "service": "http"
  },
  {
    "ip": "192.168.1.2",
    "port": 443,
    "service": "https"
  }
]
```
Example Output (CSV)
csv
Copy
Edit
ip,port,service
192.168.1.1,80,http
192.168.1.2,443,https
Security Context
This utility is meant to improve reporting workflows by standardizing output formats from various recon tools. Ensure data being exported does not contain sensitive or regulated information before sharing or publishing.

Integration
This script is commonly used after:

shodan-scanner.py – To reformat JSON output into CSV for spreadsheets

vuln_check.py – To export vulnerability matches

metadata_extractor.py – To cleanly structure findings for reporting

License
MIT License. Use at your own risk.
