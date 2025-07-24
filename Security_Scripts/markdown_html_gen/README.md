# markdown_html_gen.py
## Purpose
This script generates a Markdown report from structured scan data and saves it as a .md file. It helps transform raw scan results into a readable Markdown format for easy review or further processing.

## Features
Converts nested dictionaries and lists into Markdown sections and bullet points

Supports multiple sections with flexible content types

Saves the output as a .md file

## Requirements
Python 3.x

No external libraries required for basic Markdown generation

Optional: Install markdown package if you want to extend it for HTML conversion (not included by default)

## Installation
No installation needed for basic usage. For HTML conversion (optional):
```bash
pip install markdown
```
## Usage
```bash
python3 markdown_html_gen.py
```
By default, the script generates a sample report file named report.md.

To use with your own data, you can import the functions generate_markdown_report(data) and save_report(markdown_str, filename) into your Python projects.

## Example Input Data Structure
```python
{
  "Host Info": {
    "IP": "192.168.1.1",
    "Hostname": "example.local"
  },
  "Open Ports": [22, 80, 443],
  "Vulnerabilities": [
    "CVE-2021-41773",
    "CVE-2021-42013"
  ]
}
Example Output (report.md)
```markdown```

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
## Security Context
This script is safe and intended for report generation only. No network or file scanning is performed.

## License
MIT License. Use at your own risk.
