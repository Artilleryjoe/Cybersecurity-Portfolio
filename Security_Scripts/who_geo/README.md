## who_geo.py
Performs a Whois lookup and GeoIP geolocation query for a given domain or IP address. Outputs the combined result as structured JSON.

## Usage
python3 who_geo.py -t example.com -o who_geo_results.json

## Arguments
-t, --target: Target domain or IP address to query (required).

-o, --output: Output JSON file path (default: who_geo_results.json).

Example Output (who_geo_results.json)
  {
    "whois": {
      "domain": "example.com",
      "registrar": "Example Registrar, Inc.",
      "creation_date": "1995-08-13 04:00:00",
      "expiration_date": "2025-08-13 04:00:00",
      "name_servers": ["ns1.example.net", "ns2.example.net"],
      "emails": ["admin@example.com"]
    },
    "geoip": {
      "ip": "93.184.216.34",
      "asn": "AS15133",
      "asn_description": "EDGECAST - MCI Communications Services, Inc. d/b/a Verizon Business",
      "country": "US",
      "network_name": "EXAMPLE-NET",
      "registry": "arin"
    }
  }
## Security Context
This script is intended for legitimate security research and assessment purposes. Always ensure you have permission to query domains or IPs, especially in automated or large-scale contexts.

## Notes
Whois responses may vary by registrar and TLD.

GeoIP data is based on publicly available registry info and may not reflect precise physical location.

DNS resolution is required to query GeoIP for domain inputs.

## License
MIT License
