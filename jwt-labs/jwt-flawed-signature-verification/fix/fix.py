"""
FIX: Explicit algorithm allowlist — 'none' rejected at parse time.
"""
import jwt
from flask import Flask, request, jsonify

app = Flask(__name__)
SECRET = "super-secret-key-at-least-256-bits-long"

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): return jsonify({"error":"No token"}),401
    try:
        # FIX: algorithms=["HS256"] — 'none' not in list → rejected
        payload = jwt.decode(auth[7:], SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError as e:
        return jsonify({"error": str(e)}), 401
    if payload.get("sub") == "administrator":
        return jsonify({"message":"Welcome admin"})
    return jsonify({"error":"Forbidden"}),403
