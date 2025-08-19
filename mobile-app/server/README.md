# Mobile App Server

This folder contains a small Flask API with intentionally insecure endpoints for demonstration purposes. A disclaimer screen requires acknowledgment before the vulnerable route can be accessed.

## Endpoints

- `GET /insecure/search?name=<name>` – vulnerable SQL query built through string concatenation (disabled when `ENABLE_VULNERABLE_ENDPOINTS=false`).
- `GET /secure/search?name=<name>` – parameterized query protecting against SQL injection.

## Run Locally

```bash
cd mobile-app/server
python3 -m venv venv
source venv/bin/activate
pip install Flask
python app.py
```

The server listens on `http://localhost:8000`. When started with `ENABLE_VULNERABLE_ENDPOINTS=false`, the insecure route returns a 404.

Before exercising `/insecure/search`, visit `POST /ack` (or submit the form at the root path) to acknowledge the disclaimer. The application logs a warning if a client repeatedly submits suspicious SQL-injection payloads.

## Sample Requests

**SQL Injection against insecure endpoint**
```bash
curl "http://localhost:8000/insecure/search?name=' OR '1'='1" | jq
```

**Secure endpoint rejecting injection**
```bash
curl "http://localhost:8000/secure/search?name=' OR '1'='1" | jq
```

## Tests

Sample tests demonstrating exploitation and mitigation live under [`tests/`](tests/).
Run them with:
```bash
python tests/test_search.py
```
