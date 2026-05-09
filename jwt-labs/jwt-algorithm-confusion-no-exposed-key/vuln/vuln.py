"""
VULNERABLE: Same algorithm confusion — but RSA public key not explicitly exposed.
Attacker derives public key from two JWT tokens, then performs algo confusion.
"""
import jwt
from flask import Flask, request, jsonify

app = Flask(__name__)

# Server's key — not exposed at /jwks.json — attacker must derive it
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

_private_key = rsa.generate_private_key(65537, 2048, default_backend())
PRIVATE_KEY = _private_key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.TraditionalOpenSSL,
    serialization.NoEncryption()
)
PUBLIC_KEY = _private_key.public_key().public_bytes(
    serialization.Encoding.PEM,
    serialization.PublicFormat.SubjectPublicKeyInfo
)

@app.route("/login", methods=["POST"])
def login():
    # Returns JWT — attacker collects 2 tokens to derive public key
    return {"token": jwt.encode({"sub":"wiener","exp":9999999999},
                                PRIVATE_KEY, algorithm="RS256")}

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): return {"error":"No token"},401
    try:
        # VULN: accepts HS256 as well
        payload = jwt.decode(auth[7:], PUBLIC_KEY, algorithms=["RS256","HS256"])
    except jwt.InvalidTokenError as e:
        return {"error":str(e)},401
    if payload.get("sub") == "administrator":
        return {"message":"Welcome admin"}
    return {"error":"Forbidden"},403
