"""
VULNERABLE: Server accepts 'jwk' parameter in JWT header and uses it as the
verification key — attacker embeds their OWN public key, signs with matching
private key, server trusts it.
"""
import jwt, json, base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from flask import Flask, request, jsonify

app = Flask(__name__)

def decode_jwt_with_jwk_header(token):
    """VULN: extracts key from token's own 'jwk' header parameter."""
    header_b64 = token.split(".")[0]
    header_b64 += "=" * (-len(header_b64) % 4)
    header = json.loads(base64.urlsafe_b64decode(header_b64))

    if "jwk" not in header:
        raise ValueError("No jwk in header")

    # VULN: use the key the ATTACKER supplied in the token itself
    jwk = header["jwk"]
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
    from cryptography.hazmat.backends import default_backend

    def b64url_to_int(s):
        s += "=" * (-len(s) % 4)
        return int.from_bytes(base64.urlsafe_b64decode(s), "big")

    pub_numbers = RSAPublicNumbers(b64url_to_int(jwk["e"]), b64url_to_int(jwk["n"]))
    public_key  = pub_numbers.public_key(default_backend())
    pub_pem     = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )
    # Verifies with attacker's own key!
    return jwt.decode(token, pub_pem, algorithms=["RS256"])

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): return jsonify({"error":"No token"}),401
    try:
        payload = decode_jwt_with_jwk_header(auth[7:])
    except Exception as e:
        return jsonify({"error":str(e)}),401
    if payload.get("sub") == "administrator":
        return jsonify({"message":"Welcome admin"})
    return jsonify({"error":"Forbidden"}),403
