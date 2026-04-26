#!/usr/bin/env python3
"""
clickjacking-multistep / vuln.py
Extended detector: checks framing protection AND hunts for
multi-step confirmation flows that make the attack harder but still viable.
"""

import argparse
import sys
import re
import requests

BANNER = """
[*] Multistep Clickjacking — Vulnerability Detector
"""

CONFIRM_PATTERNS = [
    r'confirm',
    r'are you sure',
    r'do you really want',
    r'yes.*delete',
    r'type.*to confirm',
]


def check(url: str, timeout: int = 10) -> dict:
    result = {
        "url": url,
        "frameable": False,
        "has_multistep_flow": False,
        "vulnerable": False,
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

    no_xfo = xfo not in ("DENY", "SAMEORIGIN")
    no_csp_fa = "frame-ancestors" not in csp
    result["frameable"] = no_xfo and no_csp_fa

    body_lower = resp.text.lower()
    for p in CONFIRM_PATTERNS:
        if re.search(p, body_lower):
            result["has_multistep_flow"] = True
            break

    result["vulnerable"] = result["frameable"]
    return result


def main():
    print(BANNER)
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--timeout", type=int, default=10)
    args = parser.parse_args()

    r = check(args.url, args.timeout)
    print(f"  Frameable               : {'YES ⚠' if r['frameable'] else 'NO ✔'}")
    print(f"  Multi-step flow present : {'YES' if r['has_multistep_flow'] else 'NO/Unknown'}")
    print(f"  Vulnerable              : {'YES — multistep attack viable' if r['vulnerable'] else 'NO'}")
    sys.exit(0 if r["vulnerable"] else 1)


if __name__ == "__main__":
    main()
