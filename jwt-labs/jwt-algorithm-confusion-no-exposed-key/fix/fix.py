"""
FIX: Same as Lab 7 — pin RS256 algorithm. Key derivation irrelevant if
algorithm confusion is closed.
"""
import jwt
from flask import Flask, request, jsonify

app = Flask(__name__)
PUBLIC_KEY = open("server_public.pem").read()

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): return jsonify({"error":"No token"}),401
    try:
        # FIX: RS256 only — HS256 rejected regardless of whether key is known
        payload = jwt.decode(auth[7:], PUBLIC_KEY, algorithms=["RS256"])
    except jwt.InvalidTokenError as e:
        return jsonify({"error":str(e)}),401
    if payload.get("sub") == "administrator":
        return jsonify({"message":"Welcome admin"})
    return jsonify({"error":"Forbidden"}),403
