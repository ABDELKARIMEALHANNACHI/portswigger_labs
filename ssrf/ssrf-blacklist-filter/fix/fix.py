"""
FIXED CODE — SSRF with Blacklist-Based Input Filter
Language: Python (Flask)

THE CORRECT APPROACH — Never use a blacklist for SSRF.
Instead apply ALL of these layers:

FIX 1 — Allowlist: only permit known-good hostnames.
FIX 2 — Decode first: URL-decode the input before any check.
FIX 3 — Resolve DNS: resolve the hostname to an IP and check
         the resolved IP against private ranges.
FIX 4 — HTTPS only: reject all non-HTTPS schemes.
FIX 5 — No redirects: disable redirect following.
FIX 6 — Timeout: short timeout prevents timing-based scanning.

WHY EACH FIX IS NEEDED:
    Without FIX 1 (allowlist):  Direct IP injection works.
    Without FIX 2 (decode first): Encoding tricks bypass all checks.
    Without FIX 3 (DNS resolve): DNS-based bypasses (localtest.me, nip.io) work.
    Without FIX 4 (scheme):     file:// and gopher:// attacks work.
    Without FIX 5 (redirects):  Open-redirect chains bypass the allowlist.
    Without FIX 6 (timeout):    Timing-based port scanning works.
"""

from flask import Flask, request, jsonify, abort
import requests
import ipaddress
import socket
from urllib.parse import urlparse, unquote

app = Flask(__name__)

# ✅ FIX 1 — Explicit allowlist of permitted hostnames
ALLOWED_HOSTS = {
    "stock.weliketoshop.net",
    "stock-service.internal",
}

# Private/internal IP ranges to block after DNS resolution
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),       # loopback
    ipaddress.ip_network("10.0.0.0/8"),         # RFC 1918
    ipaddress.ip_network("172.16.0.0/12"),      # RFC 1918
    ipaddress.ip_network("192.168.0.0/16"),     # RFC 1918
    ipaddress.ip_network("169.254.0.0/16"),     # link-local (cloud metadata)
    ipaddress.ip_network("::1/128"),            # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),           # IPv6 private
    ipaddress.ip_network("fe80::/10"),          # IPv6 link-local
]


def is_safe_url(url: str) -> bool:
    """
    Multi-layer URL validation.
    Rejects anything that could target internal resources.
    """
    try:
        # ✅ FIX 2 — Fully decode the URL before any check
        # This defeats encoding tricks: %2561dmin → %61dmin → admin
        # We decode recursively until the URL stops changing
        decoded = url
        while True:
            next_decode = unquote(decoded)
            if next_decode == decoded:
                break
            decoded = next_decode

        parsed = urlparse(decoded)

        # ✅ FIX 4 — HTTPS scheme only
        if parsed.scheme not in ("https",):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # ✅ FIX 1 — Strict allowlist check (exact hostname match)
        # This is checked AFTER decoding so encoding tricks cannot bypass it
        if hostname.lower() not in ALLOWED_HOSTS:
            return False

        # ✅ FIX 3 — Resolve hostname to IP and verify it is not internal
        # This defeats DNS tricks: localtest.me → 127.0.0.1 → BLOCKED
        try:
            resolved_ip_str = socket.gethostbyname(hostname)
            resolved_ip = ipaddress.ip_address(resolved_ip_str)
        except socket.gaierror:
            return False  # Cannot resolve → reject

        for blocked_network in BLOCKED_NETWORKS:
            if resolved_ip in blocked_network:
                return False

        return True

    except Exception:
        return False


@app.route("/product/stock", methods=["POST"])
def check_stock():
    stock_api_url = request.form.get("stockApi", "")

    if not stock_api_url:
        abort(400, "stockApi parameter is required")

    # ✅ Validate before any network activity
    if not is_safe_url(stock_api_url):
        abort(400, "Invalid or disallowed URL")

    # ✅ FIX 5 — No redirects (blocks open-redirect bypass chains)
    # ✅ FIX 6 — Short timeout (limits timing-based scanning)
    try:
        response = requests.get(
            stock_api_url,
            allow_redirects=False,
            timeout=5,
        )

        # Block redirects at response level too
        if response.is_redirect:
            abort(400, "Redirects are not permitted")

        return jsonify({"stock": response.text}), 200

    except requests.RequestException:
        abort(502, "Could not reach stock service")


# ============================================================
# HOW THIS FIX DEFEATS EVERY BYPASS ATTEMPTED IN THE LAB
#
# Bypass attempt: http://2130706433/%2561dmin/delete?username=carlos
#
#   FIX 2 (decode): %2561dmin → %61dmin → admin  (decoded first)
#   FIX 4 (scheme): http:// is not https → REJECT
#
# Bypass attempt: https://2130706433/admin
#
#   FIX 1 (allowlist): "2130706433" not in ALLOWED_HOSTS → REJECT
#
# Bypass attempt: https://stock.weliketoshop.net@127.0.0.1/admin
#
#   FIX 2 (decode): no encoding
#   FIX 1 (allowlist): hostname parsed as "127.0.0.1" (after @) → not in ALLOWED_HOSTS → REJECT
#   (Some parsers extract the real host as the part after @)
#
# Bypass attempt: https://localtest.me/admin
#
#   FIX 1 (allowlist): "localtest.me" not in ALLOWED_HOSTS → REJECT
#
# Bypass attempt: https://stock.weliketoshop.net/admin (if stock host is on allowlist)
#
#   FIX 3 (DNS): resolve stock.weliketoshop.net → public IP → NOT in blocked networks → PASS
#   This is the ONLY URL that passes all checks: the real stock service.
# ============================================================


if __name__ == "__main__":
    app.run(debug=False)
