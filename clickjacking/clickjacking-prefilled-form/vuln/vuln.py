#!/usr/bin/env python3
"""
clickjacking-prefilled-form / vuln.py
Tests:
  1. Standard clickjacking (no XFO/CSP)
  2. Whether URL params can pre-fill form fields (reflected input values)
"""

import argparse
import sys
import re
import requests
from urllib.parse import urlencode, urljoin

BANNER = """
[*] Prefilled Form Clickjacking — Vulnerability Detector
"""

SENTINEL = "XSS_CANARY_12345"


def check(url: str, param: str = "email", value: str = None, timeout: int = 10) -> dict:
    result = {
        "url": url,
        "frameable": False,
        "param_reflected_in_form": False,
        "vulnerable": False,
        "param": param,
        "value": value or SENTINEL,
    }

    test_url = f"{url}?{param}={result['value']}"

    try:
        resp = requests.get(test_url, timeout=timeout, allow_redirects=True)
    except requests.exceptions.RequestException as exc:
        print(f"[!] {exc}")
        return result

    h = {k.lower(): v for k, v in resp.headers.items()}
    xfo = h.get("x-frame-options", "").upper()
    csp = h.get("content-security-policy", "")

    result["frameable"] = (
        xfo not in ("DENY", "SAMEORIGIN") and
        "frame-ancestors" not in csp
    )

    # Check if param value is reflected inside an input value attribute
    patterns = [
        rf'value\s*=\s*["\']?{re.escape(result["value"])}',
        rf'<input[^>]+{re.escape(result["value"])}',
    ]
    for p in patterns:
        if re.search(p, resp.text, re.IGNORECASE):
            result["param_reflected_in_form"] = True
            break

    result["vulnerable"] = result["frameable"] and result["param_reflected_in_form"]
    return result


def main():
    print(BANNER)
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Target page URL (e.g. https://lab.../my-account)")
    parser.add_argument("--param", default="email", help="Parameter name to test (default: email)")
    parser.add_argument("--value", default=None, help="Test value (default: canary string)")
    parser.add_argument("--timeout", type=int, default=10)
    args = parser.parse_args()

    r = check(args.url, args.param, args.value, args.timeout)

    print(f"  Target URL          : {r['url']}")
    print(f"  Test param          : {r['param']}={r['value']}")
    print(f"  Frameable           : {'YES ⚠' if r['frameable'] else 'NO ✔'}")
    print(f"  Param reflected     : {'YES ⚠' if r['param_reflected_in_form'] else 'NO'}")
    print(f"  Vulnerable          : {'YES — prefill + clickjack viable!' if r['vulnerable'] else 'NO'}")
    sys.exit(0 if r["vulnerable"] else 1)


if __name__ == "__main__":
    main()
