"""
VULNERABLE: Server fetches JWKS from the URL specified in the token's 'jku' header.
Attacker hosts their own JWKS at an attacker-controlled URL.
"""
import jwt, json, requests, base64
from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

app = Flask(__name__)

def b64url_to_int(s):
    s += "=" * (-len(s) % 4)
    return int.from_bytes(base64.urlsafe_b64decode(s), "big")

def get_key_from_jku(token):
    """VULN: fetch JWKS from attacker-controlled URL in token header."""
    parts = token.split(".")
    header_b64 = parts[0] + "=" * (-len(parts[0]) % 4)
    header = json.loads(base64.urlsafe_b64decode(header_b64))
    jku_url = header.get("jku")
    if not jku_url:
        raise ValueError("No jku")
    # VULN: no validation of jku URL — fetches from attacker.com
    jwks = requests.get(jku_url, timeout=5).json()
    key_data = jwks["keys"][0]
    pub_numbers = RSAPublicNumbers(b64url_to_int(key_data["e"]), b64url_to_int(key_data["n"]))
    public_key  = pub_numbers.public_key(default_backend())
    return public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): return jsonify({"error":"No token"}),401
    try:
        pub_pem = get_key_from_jku(auth[7:])   # VULN: fetches from token's URL
        payload = jwt.decode(auth[7:], pub_pem, algorithms=["RS256"])
    except Exception as e:
        return jsonify({"error":str(e)}),401
    if payload.get("sub") == "administrator":
        return jsonify({"message":"Welcome admin"})
    return jsonify({"error":"Forbidden"}),403
