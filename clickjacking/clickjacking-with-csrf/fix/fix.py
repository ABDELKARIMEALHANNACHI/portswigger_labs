#!/usr/bin/env python3
"""
clickjacking-with-csrf / fix.py
Verifies BOTH CSRF protection AND clickjacking protection are in place.
Both are required. Either alone is insufficient for full protection.
"""

import argparse, sys, re, requests

BANNER = """
[+] Clickjacking + CSRF — Full Fix Verifier
[+] Checks: CSRF token present AND framing blocked
"""

PASS = "✔ PASS"; FAIL = "✗ FAIL"

CSRF_PATTERNS = [
    r'name\s*=\s*["\']?csrf', r'csrf[-_]token',
    r'csrfmiddlewaretoken', r'authenticity_token',
]


def verify(url, timeout=10):
    checks = {
        "csp_frame_ancestors": {"status": FAIL, "detail": ""},
        "x_frame_options":     {"status": FAIL, "detail": ""},
        "csrf_token_present":  {"status": FAIL, "detail": ""},
        "overall": False,
    }
    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True)
    except Exception as e:
        print(f"[!] {e}"); return checks

    h = {k.lower(): v for k, v in resp.headers.items()}
    xfo = h.get("x-frame-options", "").upper().strip()
    csp = h.get("content-security-policy", "")

    if xfo in ("DENY", "SAMEORIGIN"):
        checks["x_frame_options"] = {"status": PASS, "detail": f"X-Frame-Options: {xfo}"}
    else:
        checks["x_frame_options"]["detail"] = f"X-Frame-Options missing (found: '{xfo or 'none'}')"

    if "frame-ancestors" in csp and ("'none'" in csp or "'self'" in csp):
        checks["csp_frame_ancestors"] = {"status": PASS, "detail": f"CSP: {csp}"}
    else:
        checks["csp_frame_ancestors"]["detail"] = "CSP frame-ancestors missing/permissive."

    for p in CSRF_PATTERNS:
        if re.search(p, resp.text, re.IGNORECASE):
            checks["csrf_token_present"] = {"status": PASS, "detail": f"CSRF token pattern found: {p}"}
            break
    if checks["csrf_token_present"]["status"] == FAIL:
        checks["csrf_token_present"]["detail"] = "No CSRF token found in form. Consider adding one."

    framing_blocked = (
        checks["csp_frame_ancestors"]["status"] == PASS or
        checks["x_frame_options"]["status"] == PASS
    )
    checks["overall"] = framing_blocked and checks["csrf_token_present"]["status"] == PASS
    return checks


def main():
    print(BANNER)
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True); p.add_argument("--timeout", type=int, default=10)
    a = p.parse_args(); c = verify(a.url, a.timeout)

    print(f"  X-Frame-Options     [{c['x_frame_options']['status']}] {c['x_frame_options']['detail']}")
    print(f"  CSP frame-ancestors [{c['csp_frame_ancestors']['status']}] {c['csp_frame_ancestors']['detail']}")
    print(f"  CSRF Token          [{c['csrf_token_present']['status']}] {c['csrf_token_present']['detail']}")
    print()
    if c["overall"]:
        print("[✔] FULL PROTECTION VERIFIED — Both CSRF and Clickjacking protections active.")
        sys.exit(0)
    else:
        print("[✗] INCOMPLETE — Both CSP frame-ancestors AND CSRF tokens required for full protection.")
        sys.exit(1)


if __name__ == "__main__":
    main()
