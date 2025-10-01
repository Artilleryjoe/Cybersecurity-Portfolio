"""Development stub for the Blockchain Secure Logging API."""

from __future__ import annotations

import json
import random
import string
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Tuple

HOST, PORT = "0.0.0.0", 8000


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", 0))
    data = handler.rfile.read(length) if length else b"{}"
    return json.loads(data or b"{}")


def _rand_hex(prefix: str, length: int = 64) -> str:
    return f"0x{''.join(random.choices(string.hexdigits.lower(), k=length))}"


class LoggingAPI(BaseHTTPRequestHandler):
    server_version = "LoggingAPIStub/0.1"

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            _json_response(self, 200, {"status": "ok"})
        else:
            _json_response(self, 404, {"detail": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/v1/batches":
            payload = _read_json(self)
            batch_id = payload.get("batch_id", "demo-batch")
            response = {
                "batch_id": batch_id,
                "manifest_path": f"manifests/{batch_id}.manifest.json",
                "root": _rand_hex("root"),
                "prev_merkle_root": payload.get("prev_merkle_root"),
                "count": 3,
            }
            _json_response(self, 200, response)
        elif self.path == "/api/v1/anchors":
            payload = _read_json(self)
            response = {
                "batch_id": payload.get("batch_id", "demo-batch"),
                "tx_hash": _rand_hex("tx"),
                "anchor_height": 1,
            }
            _json_response(self, 200, response)
        elif self.path == "/api/v1/verifications":
            payload = _read_json(self)
            response = {
                "batch_id": payload.get("batch_id", "demo-batch"),
                "verified": True,
                "merkle_root": payload.get("merkle_root", _rand_hex("root")),
                "tx_hash": payload.get("tx_hash", _rand_hex("tx")),
            }
            _json_response(self, 200, response)
        else:
            _json_response(self, 404, {"detail": "Not found"})


def serve(address: Tuple[str, int] = (HOST, PORT)) -> None:
    with HTTPServer(address, LoggingAPI) as httpd:
        host, port = httpd.server_address
        print(f"Logging API stub listening on http://{host}:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    serve()
