"""
VULNERABLE: 'kid' (key ID) from JWT header used as a filename to read the signing key.
Path traversal in kid allows reading /dev/null (empty key → sign with empty secret).
"""
import jwt, hmac, hashlib, base64, json, os
from flask import Flask, request, jsonify

app = Flask(__name__)
KEYS_DIR = "/opt/keys/"

def get_key_by_kid(kid):
    """VULN: kid used directly as filename — path traversal possible."""
    key_path = os.path.join(KEYS_DIR, kid)   # VULN: no sanitization
    with open(key_path, "rb") as f:
        return f.read()

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): return jsonify({"error":"No token"}),401
    token = auth[7:]
    parts = token.split(".")
    header = json.loads(base64.urlsafe_b64decode(parts[0]+"=="))
    kid = header.get("kid","default")
    try:
        key = get_key_by_kid(kid)   # VULN: path traversal
        payload = jwt.decode(token, key, algorithms=["HS256"])
    except Exception as e:
        return jsonify({"error":str(e)}),401
    if payload.get("sub") == "administrator":
        return jsonify({"message":"Welcome admin"})
    return jsonify({"error":"Forbidden"}),403
