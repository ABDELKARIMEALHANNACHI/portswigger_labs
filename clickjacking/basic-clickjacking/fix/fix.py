#!/usr/bin/env python3
"""
basic-clickjacking / fix.py
Verifies that the target URL has been properly hardened against clickjacking.
Checks for:
  1. X-Frame-Options: DENY or SAMEORIGIN
  2. Content-Security-Policy: frame-ancestors 'none' or 'self'
"""

import argparse
import sys
import requests

BANNER = """
[+] Basic Clickjacking — Fix Verifier
[+] PortSwigger Labs / AppSec Hardening Check
"""

PASS = "✔ PASS"
FAIL = "✗ FAIL"


def verify_fix(url: str, timeout: int = 10) -> dict:
    checks = {
        "x_frame_options": {"status": FAIL, "detail": ""},
        "csp_frame_ancestors": {"status": FAIL, "detail": ""},
        "overall": False,
    }

    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True)
    except requests.exceptions.RequestException as exc:
        print(f"[!] Request error: {exc}")
        return checks

    headers = {k.lower(): v for k, v in resp.headers.items()}

    # ── Check 1: X-Frame-Options ──
    xfo = headers.get("x-frame-options", "").strip().upper()
    if xfo in ("DENY", "SAMEORIGIN"):
        checks["x_frame_options"]["status"] = PASS
        checks["x_frame_options"]["detail"] = f"X-Frame-Options: {xfo}"
    else:
        checks["x_frame_options"]["detail"] = (
            f"Missing or weak X-Frame-Options (found: '{xfo or 'none'}'). "
            "Expected: DENY or SAMEORIGIN"
        )

    # ── Check 2: CSP frame-ancestors ──
    csp = headers.get("content-security-policy", "")
    if "frame-ancestors" in csp:
        if "'none'" in csp or "'self'" in csp:
            checks["csp_frame_ancestors"]["status"] = PASS
            checks["csp_frame_ancestors"]["detail"] = f"CSP frame-ancestors found: {csp}"
        else:
            checks["csp_frame_ancestors"]["detail"] = (
                f"CSP frame-ancestors present but value may be permissive: {csp}"
            )
    else:
        checks["csp_frame_ancestors"]["detail"] = "No CSP frame-ancestors directive found."

    # Overall: at least one must pass
    checks["overall"] = any(
        v["status"] == PASS
        for k, v in checks.items()
        if k != "overall"
    )
    return checks


def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="Verify clickjacking fix headers.")
    parser.add_argument("--url", required=True, help="Target URL to verify")
    parser.add_argument("--timeout", type=int, default=10)
    args = parser.parse_args()

    checks = verify_fix(args.url, args.timeout)

    print(f"  X-Frame-Options   [{checks['x_frame_options']['status']}]  {checks['x_frame_options']['detail']}")
    print(f"  CSP frame-ancestors [{checks['csp_frame_ancestors']['status']}]  {checks['csp_frame_ancestors']['detail']}")
    print()

    if checks["overall"]:
        print("[✔] FIX VERIFIED — Target is protected against clickjacking.")
        sys.exit(0)
    else:
        print("[✗] FIX INCOMPLETE — Protection headers are missing or misconfigured.")
        sys.exit(1)


if __name__ == "__main__":
    main()
