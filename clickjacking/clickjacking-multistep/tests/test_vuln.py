import requests

def test_clickjacking_possible():
    r = requests.get("http://localhost:5000")
    assert "X-Frame-Options" not in r.headers
