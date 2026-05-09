"""
FIX: Never use keys from the token itself.
Server maintains a list of trusted public keys — token's 'jwk' header IGNORED.
"""
import jwt
from flask import Flask, request, jsonify

app = Flask(__name__)

# FIX: trusted public keys loaded from config/keystore — attacker cannot inject
TRUSTED_PUBLIC_KEY = open("server_public.pem").read()

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): return jsonify({"error":"No token"}),401
    try:
        # FIX: jwt.decode uses our key — ignores any 'jwk' in token header
        payload = jwt.decode(
            auth[7:], TRUSTED_PUBLIC_KEY,
            algorithms=["RS256"],
            options={"verify_exp": True}
        )
    except jwt.InvalidTokenError as e:
        return jsonify({"error":str(e)}),401
    if payload.get("sub") == "administrator":
        return jsonify({"message":"Welcome admin"})
    return jsonify({"error":"Forbidden"}),403
