import requests
from urllib.parse import urlparse

ALLOWED_HOSTS = ["stock.weliketoshop.net"]

def is_safe_url(url):
    try:
        parsed = urlparse(url)

        # 🚨 Ensure hostname exists
        if not parsed.hostname:
            return False

        # 🚨 Allowlist
        if parsed.hostname not in ALLOWED_HOSTS:
            return False

        # 🚨 Block internal hosts
        if parsed.hostname in ["localhost", "127.0.0.1"]:
            return False

        return True

    except Exception:
        return False


def check_stock(stock_api):
    if not is_safe_url(stock_api):
        return "Blocked: Invalid URL"

    response = requests.get(stock_api, timeout=3)

    return response.text
