#!/usr/bin/env python3
"""Prefilled form clickjacking fix verifier."""

import argparse, sys, requests

PASS = "✔ PASS"; FAIL = "✗ FAIL"

def verify(url, timeout=10):
    checks = {"csp": {"status": FAIL, "detail": ""}, "xfo": {"status": FAIL, "detail": ""}, "overall": False}
    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True)
    except Exception as e:
        print(f"[!] {e}"); return checks
    h = {k.lower(): v for k, v in resp.headers.items()}
    xfo = h.get("x-frame-options", "").upper().strip()
    csp = h.get("content-security-policy", "")
    if xfo in ("DENY", "SAMEORIGIN"):
        checks["xfo"] = {"status": PASS, "detail": f"X-Frame-Options: {xfo}"}
    else:
        checks["xfo"]["detail"] = "X-Frame-Options missing or weak."
    if "frame-ancestors" in csp and ("'none'" in csp or "'self'" in csp):
        checks["csp"] = {"status": PASS, "detail": f"CSP: {csp}"}
    else:
        checks["csp"]["detail"] = "CSP frame-ancestors missing/permissive."
    checks["overall"] = checks["csp"]["status"] == PASS or checks["xfo"]["status"] == PASS
    return checks

def main():
    print("\n[+] Prefilled Form Clickjacking — Fix Verifier\n")
    p = argparse.ArgumentParser(); p.add_argument("--url", required=True); p.add_argument("--timeout", type=int, default=10)
    a = p.parse_args(); c = verify(a.url, a.timeout)
    print(f"  X-Frame-Options     [{c['xfo']['status']}] {c['xfo']['detail']}")
    print(f"  CSP frame-ancestors [{c['csp']['status']}] {c['csp']['detail']}")
    if c["overall"]: print("\n[✔] FIX VERIFIED"); sys.exit(0)
    else: print("\n[✗] FIX INCOMPLETE"); sys.exit(1)

if __name__ == "__main__":
    main()
