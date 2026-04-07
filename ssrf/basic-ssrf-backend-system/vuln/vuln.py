"""
VULNERABLE CODE — Basic SSRF Against Another Back-End System
Language: Python (Flask)

WHY THIS IS VULNERABLE:
    The `stockApi` parameter is taken directly from the POST body
    and passed to requests.get() with zero validation.
    An attacker can supply any URL — including internal IPs
    like http://192.168.0.X:8080/admin — and the server will
    faithfully fetch it and return the response.
"""

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


@app.route("/product/stock", methods=["POST"])
def check_stock():
    # ❌ VULNERABLE: User-supplied URL fetched with no validation
    stock_api_url = request.form.get("stockApi")

    # The server makes a request to whatever URL the attacker provides
    # This includes: http://192.168.0.X:8080/admin
    response = requests.get(stock_api_url)

    return jsonify({"stock": response.text}), response.status_code


# ============================================================
# HOW THE ATTACK WORKS AGAINST THIS CODE
#
# Normal request:
#   stockApi=https://stock.internal/product/123
#   → Server fetches legitimate stock data
#
# Attack — host discovery:
#   stockApi=http://192.168.0.1:8080/admin   (repeat for 1–255)
#   → Server fetches internal admin panel
#   → One IP returns 200 with admin panel HTML
#
# Attack — delete user:
#   stockApi=http://192.168.0.68:8080/admin/delete?username=carlos
#   → Server makes request to internal admin
#   → Admin deletes carlos (trusts any internal request)
#   → 302 redirect returned
# ============================================================


if __name__ == "__main__":
    app.run(debug=True)
