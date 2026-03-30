import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/stock", methods=["POST"])
def check_stock():
    stock_api = request.form.get("stockApi")

    try:
        # 🚨 VULNERABLE: direct request to user-controlled URL
        r = requests.get(stock_api, timeout=2)
        return jsonify({
            "status": r.status_code,
            "data": r.text[:200]
        })

    except requests.exceptions.RequestException:
        return jsonify({"error": "Request failed"}), 500


if __name__ == "__main__":
    app.run(debug=True)
