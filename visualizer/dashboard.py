#!/usr/bin/env python3
"""Local-only live dashboard for the Equifax S2-045 classroom lab."""
import json
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVENTS = deque(maxlen=40)
MAX_BODY = 4096

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/state":
            self.send_json(200, {"events": list(EVENTS)})
        elif self.path in ("/", "/index.html"):
            self.send_file("index.html", "text/html; charset=utf-8")
        elif self.path == "/app.js":
            self.send_file("app.js", "text/javascript; charset=utf-8")
        elif self.path == "/styles.css":
            self.send_file("styles.css", "text/css; charset=utf-8")
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/events":
            self.send_json(404, {"error": "not found"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 1 or size > MAX_BODY:
                raise ValueError("event size is not allowed")
            event = json.loads(self.rfile.read(size))
            port, status = int(event["port"]), int(event["status"])
            proof, target = str(event.get("proof", ""))[:80], str(event["target"])[:80]
            if port not in (8080, 8081) or not (100 <= status <= 599):
                raise ValueError("invalid lab result")
            if any(ch not in "0123456789abcdefABCDEF:." for ch in target):
                raise ValueError("target must be an IP address")
            if status == 200 and proof == "54289":
                result, action = "proof", "Forwarded to the vulnerable training target"
            elif status == 403:
                result, action = "blocked", "Blocked by the lab guard"
            else:
                result, action = "other", "No expected proof or block result"
            EVENTS.appendleft({
                "time": datetime.now(timezone.utc).strftime("%H:%M:%S UTC"),
                "target": target, "port": port, "status": status,
                "proof": proof if proof else "absent", "result": result, "action": action,
            })
            self.send_json(201, {"ok": True})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            self.send_json(400, {"error": str(error)})

    def send_file(self, filename, content_type):
        data = (HERE / filename).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, status, value):
        data = json.dumps(value).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, _format, *_args):
        return

if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8090), Handler)
    print("Equifax lab dashboard: http://127.0.0.1:8090")
    print("Local-only view. Start the terminal demo in another window.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()
