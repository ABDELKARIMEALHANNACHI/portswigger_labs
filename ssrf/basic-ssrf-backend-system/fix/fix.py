import requests
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
