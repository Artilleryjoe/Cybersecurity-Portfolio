# vuln_check.py

## Purpose

Matches discovered services and versions against a lightweight CVE database to highlight potential vulnerabilities.

## Features

- Accepts service scan results in JSON format.
- Maps each service/version pair to known CVEs.
- Outputs a concise JSON report of vulnerable services.
- Supports writing results to a file or printing to the console.

## Requirements

- Python 3.x

## Usage

```bash
python3 vuln_check.py -i shodan_results.json -o vuln_report.json
```

Arguments

`-i, --input` – JSON file containing service scan data

`-o, --output` – Optional path to save the vulnerability report

## Example Output (snippet)

```json
[
  {
    "host": "198.51.100.23",
    "port": 80,
    "service": "Apache httpd",
    "version": "2.4.41",
    "cves": ["CVE-2021-41773", "CVE-2021-42013"]
  }
]
```

## Security Context

Use only on systems you are authorized to test. Validate findings before taking action.

## License

MIT License

