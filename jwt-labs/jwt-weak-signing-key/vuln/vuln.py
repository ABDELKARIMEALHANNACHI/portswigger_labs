"""
VULNERABLE: HS256 JWT signed with a weak/common secret (e.g. "secret", "password").
Attacker brute-forces the secret with hashcat, then forges arbitrary tokens.
"""
import jwt
from flask import Flask, request, jsonify

app = Flask(__name__)

# VULN: Predictable, short, common secret — in hashcat's wordlist
SECRET = "secret"

def create_token(username):
    return jwt.encode({"sub": username, "exp": 9999999999}, SECRET, algorithm="HS256")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if data.get("username") == "wiener" and data.get("password") == "peter":
        return jsonify({"token": create_token("wiener")})
    return jsonify({"error": "Invalid"}), 401

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): return jsonify({"error":"No token"}),401
    try:
        payload = jwt.decode(auth[7:], SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return jsonify({"error":"Invalid token"}),401
    if payload.get("sub") == "administrator":
        return jsonify({"message":"Welcome admin","data":"sensitive"})
    return jsonify({"error":"Forbidden"}),403

if __name__ == "__main__":
    app.run(debug=True)
