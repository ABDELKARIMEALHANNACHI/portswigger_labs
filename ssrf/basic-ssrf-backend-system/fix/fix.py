"""
FIXED CODE — Basic SSRF Against Another Back-End System
Language: Python (Flask)

FIXES APPLIED:
    1. Allowlist — only the known stock service hostname is permitted
    2. DNS resolution check — resolve the hostname and verify the IP
       is not in any private/internal range before making the request
    3. Scheme enforcement — only HTTPS allowed
    4. Redirect following disabled — prevents open-redirect bypass
    5. Timeout enforced — prevents hanging on slow internal services
"""

from flask import Flask, request, jsonify, abort
import requests
import ipaddress
import socket
from urllib.parse import urlparse

app = Flask(__name__)

# ✅ FIX 1 — Strict allowlist of permitted hostnames
ALLOWED_HOSTS = {
    "stock.internal",
    "stock-service.production.internal",
}

# ✅ FIX 2 — Private/internal IP ranges to block
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),       # loopback
    ipaddress.ip_network("10.0.0.0/8"),         # private
    ipaddress.ip_network("172.16.0.0/12"),      # private
    ipaddress.ip_network("192.168.0.0/16"),     # private
    ipaddress.ip_network("169.254.0.0/16"),     # link-local (cloud metadata)
    ipaddress.ip_network("::1/128"),            # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),           # IPv6 private
]


def is_safe_url(url: str) -> bool:
    """
    Validate the URL before the server fetches it.
    Returns True only if the URL passes all safety checks.
    """
    try:
        parsed = urlparse(url)

        # ✅ FIX 3 — Only allow HTTPS
        if parsed.scheme != "https":
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # ✅ FIX 1 — Hostname must be on the allowlist
        if hostname not in ALLOWED_HOSTS:
            return False

        # ✅ FIX 2 — Resolve hostname and check resolved IP is not internal
        # This blocks DNS-based tricks (e.g., attacker.com → 192.168.0.1)
        resolved_ip = ipaddress.ip_address(socket.gethostbyname(hostname))
        for blocked_net in BLOCKED_NETWORKS:
            if resolved_ip in blocked_net:
                return False

        return True

    except Exception:
        # Any parsing or resolution error → reject
        return False


@app.route("/product/stock", methods=["POST"])
def check_stock():
    stock_api_url = request.form.get("stockApi")

    if not stock_api_url:
        abort(400, "stockApi parameter is required")

    # ✅ Validate before fetching
    if not is_safe_url(stock_api_url):
        abort(400, "Invalid or disallowed URL")

    # ✅ FIX 4 — Disable redirect following (blocks open-redirect bypass)
    # ✅ FIX 5 — Enforce timeout (prevents DoS via slow internal services)
    response = requests.get(
        stock_api_url,
        allow_redirects=False,
        timeout=5,
    )

    # ✅ Extra: Block redirects to internal addresses too
    if response.is_redirect:
        abort(400, "Redirects are not permitted")

    return jsonify({"stock": response.text}), 200


if __name__ == "__main__":
    app.run(debug=False)import requests
from urllib.parse import urlparse
import socket

ALLOWED_HOSTS = ["stock.weliketoshop.net"]

def is_safe(url):
    try:
        parsed = urlparse(url)

        if not parsed.hostname:
            return False

        if parsed.hostname not in ALLOWED_HOSTS:
            return False

        ip = socket.gethostbyname(parsed.hostname)

        # Block private ranges
        if ip.startswith("127.") or ip.startswith("192.168.") or ip.startswith("10."):
            return False

        return True

    except:
        return False


def check_stock(stock_api):
    if not is_safe(stock_api):
        return "Blocked"

    r = requests.get(stock_api, timeout=2)
    return r.text
