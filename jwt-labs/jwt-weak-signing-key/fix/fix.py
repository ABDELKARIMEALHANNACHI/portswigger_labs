"""
FIX: Use a cryptographically random secret of at least 256 bits (32 bytes).
Generated once at startup; never hardcoded.
"""
import jwt, secrets, os
from flask import Flask, request, jsonify

app = Flask(__name__)

# FIX: 256-bit random secret loaded from env — never hardcoded
SECRET = os.environ.get("JWT_SECRET") or secrets.token_hex(32)
# In production: set JWT_SECRET env var to a 32-byte random value
# Generate: python3 -c "import secrets; print(secrets.token_hex(32))"

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): return jsonify({"error":"No token"}),401
    try:
        payload = jwt.decode(auth[7:], SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError as e:
        return jsonify({"error":str(e)}),401
    if payload.get("sub") == "administrator":
        return jsonify({"message":"Welcome admin"})
    return jsonify({"error":"Forbidden"}),403
