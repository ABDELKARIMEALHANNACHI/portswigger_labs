"""
FIX: Pin JWKS URL at configuration time — never trust jku from token header.
"""
import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import requests, base64, json
from flask import Flask, request, jsonify

app = Flask(__name__)

# FIX: JWKS URL is pinned in server config — not read from token
TRUSTED_JWKS_URL = "https://auth-server.internal/jwks.json"

def load_trusted_keys():
    """Load keys from pinned, trusted JWKS endpoint at startup."""
    resp = requests.get(TRUSTED_JWKS_URL, timeout=5)
    resp.raise_for_status()
    keys = {}
    def b64url_to_int(s):
        s += "=" * (-len(s) % 4)
        return int.from_bytes(base64.urlsafe_b64decode(s),"big")
    for k in resp.json()["keys"]:
        pub = RSAPublicNumbers(b64url_to_int(k["e"]), b64url_to_int(k["n"]))
        pem = pub.public_key(default_backend()).public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        keys[k["kid"]] = pem
    return keys

TRUSTED_KEYS = load_trusted_keys()   # loaded once at startup from trusted URL

def verify_token(token):
    header = json.loads(base64.urlsafe_b64decode(
        token.split(".")[0] + "=="))
    kid = header.get("kid")
    # FIX: kid must match a key we loaded from OUR trusted JWKS URL
    key = TRUSTED_KEYS.get(kid)
    if not key:
        raise ValueError(f"Unknown kid: {kid}")
    return jwt.decode(token, key, algorithms=["RS256"])

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): return jsonify({"error":"No token"}),401
    try:
        payload = verify_token(auth[7:])
    except Exception as e:
        return jsonify({"error":str(e)}),401
    if payload.get("sub") == "administrator":
        return jsonify({"message":"Welcome admin"})
    return jsonify({"error":"Forbidden"}),403
