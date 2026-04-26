#!/usr/bin/env python3
"""
clickjacking-frame-buster-bypass / vuln.py
Detects:
  1. Whether the site is frameable (no X-Frame-Options / CSP frame-ancestors)
  2. Whether the page uses a JavaScript frame buster (detectable in source)
  3. Whether the sandbox bypass would work (frame buster present but no CSP)
"""

import argparse
import sys
import re
import requests

BANNER = """
[*] Frame-Buster Bypass — Vulnerability Detector
[*] PortSwigger Labs / Educational Use Only
"""

FRAME_BUSTER_PATTERNS = [
    r"top\.location\s*=\s*self\.location",
    r"top\.location\.href\s*=",
    r"if\s*\(\s*top\s*!==?\s*self\s*\)",
    r"if\s*\(\s*window\.top\s*!==?\s*window\.self\s*\)",
    r"window\.frameElement",
    r"parent\s*!==?\s*window",
]


def check(url: str, timeout: int = 10) -> dict:
    result = {
        "url": url,
        "frameable": False,
        "has_frame_buster_js": False,
        "sandbox_bypass_possible": False,
        "headers": {},
        "frame_buster_snippets": [],
    }

    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True)
    except requests.exceptions.RequestException as exc:
        print(f"[!] Request error: {exc}")
        return result

    headers = {k.lower(): v for k, v in resp.headers.items()}
    result["headers"] = dict(resp.headers)

    xfo = headers.get("x-frame-options", "").strip().upper()
    csp = headers.get("content-security-policy", "")

    # Frameable check
    no_xfo = xfo not in ("DENY", "SAMEORIGIN")
    no_csp = "frame-ancestors" not in csp or (
        "'none'" not in csp and "'self'" not in csp
    )
    result["frameable"] = no_xfo and no_csp

    # JS frame buster check
    body = resp.text
    for pattern in FRAME_BUSTER_PATTERNS:
        matches = re.findall(pattern, body)
        if matches:
            result["has_frame_buster_js"] = True
            result["frame_buster_snippets"].extend(matches)

    # Sandbox bypass is possible if frameable AND frame buster only in JS (no CSP)
    result["sandbox_bypass_possible"] = (
        result["frameable"] and result["has_frame_buster_js"]
    )

    return result


def main():
    print(BANNER)
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    r = check(args.url, args.timeout)

    print(f"  Frameable (no XFO/CSP)   : {'YES ⚠' if r['frameable'] else 'NO ✔'}")
    print(f"  JS Frame Buster present  : {'YES' if r['has_frame_buster_js'] else 'NO'}")
    print(f"  Sandbox bypass possible  : {'YES ⚠⚠ VULNERABLE' if r['sandbox_bypass_possible'] else 'NO'}")

    if r["frame_buster_snippets"]:
        print("\n  Frame Buster patterns found:")
        for s in set(r["frame_buster_snippets"]):
            print(f"    → {s}")

    if args.verbose:
        print("\n  Response Headers:")
        for k, v in r["headers"].items():
            print(f"    {k}: {v}")

    sys.exit(0 if r["sandbox_bypass_possible"] else 1)


if __name__ == "__main__":
    main()
