import requests

def test_protection():
    r = requests.get("http://localhost:5000")
    assert r.headers.get("X-Frame-Options") == "DENY"
