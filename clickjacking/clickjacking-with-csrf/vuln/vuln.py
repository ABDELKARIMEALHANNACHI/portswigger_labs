#!/usr/bin/env python3
"""
clickjacking-with-csrf / vuln.py
Detects:
  1. Whether the page has a CSRF token (common false sense of security)
  2. Whether the page is STILL frameable (making CSRF bypass via clickjacking viable)
"""

import argparse
import sys
import re
import requests

BANNER = """
[*] Clickjacking + CSRF Bypass — Vulnerability Detector
[*] Tests whether CSRF-protected pages are still frameable
"""

CSRF_PATTERNS = [
    r'name\s*=\s*["\']?csrf',
    r'name\s*=\s*["\']?_token',
    r'name\s*=\s*["\']?__RequestVerificationToken',
    r'csrf[-_]token',
    r'csrfmiddlewaretoken',
    r'X-CSRF-Token',
    r'authenticity_token',
]


def check(url: str, timeout: int = 10) -> dict:
    result = {
        "url": url,
        "has_csrf_token": False,
        "frameable": False,
        "clickjack_bypasses_csrf": False,
        "csrf_patterns_found": [],
        "headers": {},
    }

    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True)
    except requests.exceptions.RequestException as exc:
        print(f"[!] {exc}")
        return result

    h = {k.lower(): v for k, v in resp.headers.items()}
    result["headers"] = dict(resp.headers)

    xfo = h.get("x-frame-options", "").upper().strip()
    csp = h.get("content-security-policy", "")

    result["frameable"] = (
        xfo not in ("DENY", "SAMEORIGIN") and
        "frame-ancestors" not in csp
    )

    body = resp.text
    for p in CSRF_PATTERNS:
        if re.search(p, body, re.IGNORECASE):
            result["has_csrf_token"] = True
            result["csrf_patterns_found"].append(p)

    result["clickjack_bypasses_csrf"] = (
        result["frameable"] and result["has_csrf_token"]
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

    print(f"  Target URL                : {r['url']}")
    print(f"  CSRF token present        : {'YES' if r['has_csrf_token'] else 'NO'}")
    print(f"  Frameable (no XFO/CSP)    : {'YES ⚠' if r['frameable'] else 'NO ✔'}")
    print(f"  Clickjack bypasses CSRF   : {'YES ⚠⚠ CRITICAL' if r['clickjack_bypasses_csrf'] else 'NO'}")

    if r["csrf_patterns_found"] and args.verbose:
        print("\n  CSRF patterns detected:")
        for p in set(r["csrf_patterns_found"]):
            print(f"    → {p}")

    if r["clickjack_bypasses_csrf"]:
        print("""
  [!] FINDING: CSRF tokens are present but the page is frameable.
      An attacker can bypass CSRF protection via clickjacking:
      The iframe loads the victim's session including the valid CSRF token.
      The victim's click submits the form with the authentic CSRF token.
      Server accepts the request as legitimate.
  """)

    sys.exit(0 if r["clickjack_bypasses_csrf"] else 1)


if __name__ == "__main__":
    main()
