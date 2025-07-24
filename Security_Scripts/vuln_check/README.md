# markdown_html_gen.py

## Purpose

Converts structured scan or analysis data into a Markdown-formatted `.md` report file. Useful for quickly creating readable summaries from tool output like vulnerability scans or system inspections.

## Features

- Accepts nested dictionaries and lists
- Outputs clean, human-readable Markdown reports
- Generates headers for each section and key-value bullet lists

## Requirements

- Python 3.x

## Installation

No external libraries required.

## Usage

Run the script directly with embedded sample data:

```bash
python3 markdown_html_gen.py
```
To use with your own data:

```python
from markdown_html_gen import generate_markdown_report, save_report

my_data = {
    "Host Info": {"IP": "10.0.0.1", "Hostname": "target.local"},
    "Services": ["SSH", "HTTP", "HTTPS"],
    "Issues Found": ["CVE-2023-12345", "CVE-2023-67890"]
}
```
markdown = generate_markdown_report(my_data)

save_report(markdown, "my_scan_report.md")

## Example Output (Markdown)
```markdown
# Scan Report

## Host Info
- **IP**: 192.168.1.1
- **Hostname**: example.local

## Open Ports
- 22
- 80
- 443

## Vulnerabilities
- CVE-2021-41773
- CVE-2021-42013
```
## Integration
Use this after:

- `csv_json_export.py` or `exploit_checker.py` to convert JSON findings into Markdown

- Manual aggregation of findings for simple reporting

## License
MIT License. Use at your own risk.
