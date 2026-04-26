#!/usr/bin/env python3
"""
basic-clickjacking / vuln.py
Detects whether the target URL is vulnerable to basic clickjacking
by inspecting HTTP response headers.
"""

import argparse
import sys
import requests
from urllib.parse import urlparse

BANNER = r"""
  ___ _ _     _   _  _         _    _
 / __| (_) __| |_(_)__ _ __  | |__(_)_ _  ___ __ __
| (__| | |/ _| / / / _` / _` | / /| | ' \/ -_) \ /
 \___|_|_|\__|_\_\_\__,_\__, |_\_\|_|_||_\___/_\_\
                         |___/
[*] Basic Clickjacking Vulnerability Detector
[*] PortSwigger Labs — Educational Use Only
"""


def check_clickjacking(url: str, timeout: int = 10) -> dict:
    """
    Returns a dict with:
      vulnerable (bool), headers (dict), reason (str)
    """
    result = {"url": url, "vulnerable": False, "headers": {}, "reason": ""}

    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True)
    except requests.exceptions.RequestException as exc:
        result["reason"] = f"Request failed: {exc}"
        return result

    headers = {k.lower(): v for k, v in resp.headers.items()}
    result["headers"] = dict(resp.headers)

    xfo = headers.get("x-frame-options", "")
    csp = headers.get("content-security-policy", "")

    # Evaluate X-Frame-Options
    if xfo.strip().upper() in ("DENY", "SAMEORIGIN"):
        result["reason"] = f"X-Frame-Options: {xfo} — framing blocked."
        return result

    # Evaluate CSP frame-ancestors
    if "frame-ancestors" in csp:
        if "'none'" in csp or "frame-ancestors 'self'" in csp:
            result["reason"] = f"CSP frame-ancestors present: {csp}"
            return result

    # No protection found
    result["vulnerable"] = True
    result["reason"] = (
        "No X-Frame-Options or CSP frame-ancestors header detected. "
        "Site is likely frameable — vulnerable to clickjacking."
    )
    return result


def main():
    print(BANNER)
    parser = argparse.ArgumentParser(
        description="Detect basic clickjacking vulnerability via header analysis."
    )
    parser.add_argument("--url", required=True, help="Target URL (e.g. https://lab.web-security-academy.net)")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    parser.add_argument("--verbose", action="store_true", help="Print all response headers")
    args = parser.parse_args()

    result = check_clickjacking(args.url, args.timeout)

    print(f"[*] Target  : {result['url']}")
    print(f"[*] Status  : {'⚠  VULNERABLE' if result['vulnerable'] else '✔  NOT VULNERABLE'}")
    print(f"[*] Reason  : {result['reason']}")

    if args.verbose:
        print("\n[*] Response Headers:")
        for k, v in result["headers"].items():
            print(f"    {k}: {v}")

    sys.exit(0 if result["vulnerable"] else 1)


if __name__ == "__main__":
    main()
