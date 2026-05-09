"""
VULNERABLE: Server accepts both RS256 and HS256 on the same endpoint.
Attack: obtain RSA public key → sign HS256 token using public key as HMAC secret.
Server's verify() call with RSA public key + HS256 matches attacker's HMAC.
"""
import jwt
from flask import Flask, request, jsonify

app = Flask(__name__)

# Server's RSA public key — legitimately exposed at /jwks.json
PUBLIC_KEY = open("server_public.pem").read()
PRIVATE_KEY = open("server_private.pem").read()

@app.route("/jwks.json")
def jwks():
    # Public key exposed here — necessary for clients to verify tokens
    return {"keys":[{"kty":"RSA","use":"sig","alg":"RS256","kid":"server-key","n":"...","e":"AQAB"}]}

@app.route("/login", methods=["POST"])
def login():
    return {"token": jwt.encode({"sub":"wiener"}, PRIVATE_KEY, algorithm="RS256")}

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): return {"error":"No token"},401
    try:
        # VULN: accepts BOTH RS256 and HS256 — algorithm confusion attack possible
        payload = jwt.decode(auth[7:], PUBLIC_KEY, algorithms=["RS256","HS256"])
    except jwt.InvalidTokenError as e:
        return {"error":str(e)},401
    if payload.get("sub") == "administrator":
        return {"message":"Welcome admin"}
    return {"error":"Forbidden"},403
