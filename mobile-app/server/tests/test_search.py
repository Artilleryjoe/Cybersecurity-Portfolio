import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app, init_db

init_db()
client = app.test_client()

# Exploitation example
payload = "' OR '1'='1"
resp_insecure = client.get(f"/insecure/search?name={payload}")
print("Insecure results:", resp_insecure.get_json())

# Mitigation example
resp_secure = client.get(f"/secure/search?name={payload}")
print("Secure results:", resp_secure.get_json())

# Assertions documenting expected behavior
assert len(resp_insecure.get_json()['results']) > 1, "Injection should list multiple users"
assert len(resp_secure.get_json()['results']) == 0, "Secure endpoint should return no results"
