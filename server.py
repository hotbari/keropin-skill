#!/usr/bin/env python3
"""keropin server - serves the UI and handles response/export file I/O."""

import http.server
import json
import os
import random
import sys

KEROPIN_DIR = os.path.dirname(os.path.abspath(__file__))
RESPONSE_FILE = "/tmp/keropin_response.md"
EXPORT_FILE = "/tmp/keropin_export.txt"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=KEROPIN_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/api/response":
            self._serve_json_file(RESPONSE_FILE)
        elif self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/export":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode()
            with open(EXPORT_FILE, "w") as f:
                f.write(body)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"saved": True}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_json_file(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"content": content}).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "not found"}).encode())

    def log_message(self, format, *args):
        pass  # silence logs


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else random.randint(10000, 59999)
    server = http.server.HTTPServer(("", port), Handler)
    print(f"http://localhost:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


if __name__ == "__main__":
    main()
