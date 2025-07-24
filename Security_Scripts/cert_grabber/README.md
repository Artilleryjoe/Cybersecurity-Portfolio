## cert_grabber.py
Fetches SSL/TLS certificate metadata from a remote host.

## Usage
```python3 cert_grabber.py -t example.com -p 443 -o cert_info.json```

## Arguments:

-t, --target: Target hostname (e.g., example.com) (required)

-p, --port: Target port (default: 443)

-o, --output: Output file for certificate metadata (default: cert_info.json)

Example Output (cert_info.json)
  '''{
    "subject": {
      "commonName": "example.com"
    },
    "issuer": {
      "commonName": "Example CA"
    },
    "serial_number": "04D2E6F9A6BC",
    "not_before": "2025-05-01T00:00:00",
    "not_after": "2026-05-01T23:59:59",
    "version": 3
  }'''
  
## Security Context
This script is for educational or authorized use only. Interrogating certificate details from unauthorized systems may violate acceptable use policies.

## Notes
Dates are converted to ISO 8601 format where possible.

If the connection or certificate fetch fails, an error message will be returned in the output JSON.

Works with most public-facing HTTPS servers.

## License
MIT License
