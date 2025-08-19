import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app, init_db

init_db()

with app.test_client() as client:
    # Acknowledge disclaimer before using vulnerable modules
    client.post('/ack')

    payload = "' OR '1'='1'"
    for _ in range(4):
        resp_insecure = client.get(f"/insecure/search?name={payload}")
    print("Insecure results:", resp_insecure.get_json())

    resp_secure = client.get(f"/secure/search?name={payload}")
    print("Secure results:", resp_secure.get_json())

    assert len(resp_insecure.get_json()['results']) > 1, "Injection should list multiple users"
    assert len(resp_secure.get_json()['results']) == 0, "Secure endpoint should return no results"

