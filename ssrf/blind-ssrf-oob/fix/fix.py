import requests
from urllib.parse import urlparse

ALLOWED_DOMAINS = ["vulnerable-lab.net"]

def is_safe(url):
    parsed = urlparse(url)
    return parsed.hostname in ALLOWED_DOMAINS

def fetch_product_safe(url, referer):
    if not is_safe(referer):
        raise Exception("Blocked SSRF in Referer header")

    headers = {
        "Referer": referer
    }

    return requests.get(url, headers=headers).text
