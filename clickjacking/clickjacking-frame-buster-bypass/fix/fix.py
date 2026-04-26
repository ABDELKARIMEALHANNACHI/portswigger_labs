#!/usr/bin/env python3
"""
Frame-Buster Bypass / fix.py
Verifies the CORRECT fix: CSP frame-ancestors (NOT relying on JS frame busters).
Also warns if the site still relies on a JS frame buster without CSP.
"""

import argparse
import sys
import re
import requests

BANNER = """
[+] Frame-Buster Bypass — Fix Verifier
[+] Correct fix = CSP frame-ancestors, NOT JavaScript busters
"""

PASS = "✔ PASS"
FAIL = "✗ FAIL"
WARN = "⚠ WARN"


def verify(url: str, timeout: int = 10) -> dict:
    checks = {
        "csp_frame_ancestors": {"status": FAIL, "detail": ""},
        "x_frame_options": {"status": FAIL, "detail": ""},
        "js_buster_only": {"status": WARN, "detail": ""},
        "overall": False,
    }

    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True)
    except requests.exceptions.RequestException as exc:
        print(f"[!] {exc}")
        return checks

    h = {k.lower(): v for k, v in resp.headers.items()}
    xfo = h.get("x-frame-options", "").upper().strip()
    csp = h.get("content-security-policy", "")

    if "frame-ancestors" in csp and ("'none'" in csp or "'self'" in csp):
        checks["csp_frame_ancestors"]["status"] = PASS
        checks["csp_frame_ancestors"]["detail"] = f"CSP: {csp}"
    else:
        checks["csp_frame_ancestors"]["detail"] = "CSP frame-ancestors not set or permissive."

    if xfo in ("DENY", "SAMEORIGIN"):
        checks["x_frame_options"]["status"] = PASS
        checks["x_frame_options"]["detail"] = f"X-Frame-Options: {xfo}"
    else:
        checks["x_frame_options"]["detail"] = f"X-Frame-Options missing/weak: '{xfo or 'not set'}'"

    # Warn if page still relies solely on JS buster
    has_buster = bool(re.search(r"top\.location|window\.parent", resp.text))
    csp_protected = checks["csp_frame_ancestors"]["status"] == PASS
    if has_buster and not csp_protected:
        checks["js_buster_only"]["detail"] = (
            "Page uses JS frame buster but no CSP — sandbox bypass still possible!"
        )
    elif has_buster and csp_protected:
        checks["js_buster_only"]["status"] = PASS
        checks["js_buster_only"]["detail"] = "JS buster present but CSP provides real protection."
    else:
        checks["js_buster_only"]["status"] = PASS
        checks["js_buster_only"]["detail"] = "No JS buster dependency detected."

    checks["overall"] = checks["csp_frame_ancestors"]["status"] == PASS or \
                        checks["x_frame_options"]["status"] == PASS

    return checks


def main():
    print(BANNER)
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--timeout", type=int, default=10)
    args = parser.parse_args()

    c = verify(args.url, args.timeout)
    print(f"  CSP frame-ancestors [{c['csp_frame_ancestors']['status']}]  {c['csp_frame_ancestors']['detail']}")
    print(f"  X-Frame-Options     [{c['x_frame_options']['status']}]  {c['x_frame_options']['detail']}")
    print(f"  JS Buster Only      [{c['js_buster_only']['status']}]  {c['js_buster_only']['detail']}")
    print()

    if c["overall"]:
        print("[✔] FIX VERIFIED")
        sys.exit(0)
    else:
        print("[✗] FIX INCOMPLETE — Add CSP frame-ancestors header.")
        sys.exit(1)


if __name__ == "__main__":
    main()
