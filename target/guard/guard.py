import json
import os
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import unquote
from urllib.request import Request, urlopen


UPSTREAM = os.environ.get("UPSTREAM", "http://struts:8080").rstrip("/")
SUSPICIOUS = re.compile(r"%\s*\{|#\s*(?:context|ognl)|ognl", re.IGNORECASE)
HOP_BY_HOP = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"}


def log_event(event):
    print(json.dumps({"time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **event}), flush=True)


class GuardHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        self.forward()

    def do_POST(self):
        self.forward()

    def do_HEAD(self):
        self.forward()

    def forward(self):
        content_type = self.headers.get("Content-Type", "")
        decoded = unquote(unquote(content_type))
        if SUSPICIOUS.search(content_type) or SUSPICIOUS.search(decoded):
            log_event({
                "source": self.client_address[0],
                "method": self.command,
                "path": self.path,
                "action": "blocked",
                "reason": "OGNL-like expression in Content-Type",
            })
            body = b"Blocked by the Equifax lab guard. See proxy logs.\n"
            self.send_response(403)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
            return

        length = min(int(self.headers.get("Content-Length", "0") or "0"), 1_048_576)
        body = self.rfile.read(length) if length else None
        headers = {
            key: value
            for key, value in self.headers.items()
            if key.lower() not in HOP_BY_HOP | {"host", "content-length"}
        }
        upstream_url = f"{UPSTREAM}{self.path}"
        request = Request(upstream_url, data=body, headers=headers, method=self.command)
        try:
            try:
                response = urlopen(request, timeout=8)
            except HTTPError as error:
                response = error
            response_body = response.read()
            self.send_response(response.status)
            for key, value in response.headers.items():
                if key.lower() not in HOP_BY_HOP and key.lower() != "content-length":
                    self.send_header(key, value)
            self.send_header("Content-Length", str(len(response_body)))
            self.send_header("Connection", "close")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(response_body)
            log_event({
                "source": self.client_address[0],
                "method": self.command,
                "path": self.path,
                "action": "forwarded",
                "upstream_status": response.status,
            })
        except (URLError, TimeoutError, OSError, ValueError) as error:
            message = f"Upstream unavailable: {error}\n".encode("utf-8", errors="replace")
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(message)))
            self.send_header("Connection", "close")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(message)
            log_event({
                "source": self.client_address[0],
                "method": self.command,
                "path": self.path,
                "action": "error",
                "error": str(error),
            })

    def log_message(self, _format, *_args):
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8081), GuardHandler)
    print("Equifax lab guard listening on port 8081", flush=True)
    server.serve_forever()
