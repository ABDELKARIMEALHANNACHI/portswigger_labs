"""
VULNERABLE: Server accepts alg='none' — skips signature verification.
This was CVE-2015-9235 (node-jsonwebtoken) and similar.
"""
import base64, json, hmac, hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)
SECRET = "super-secret-key"

def b64url_decode(s):
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)

def verify_jwt(token):
    parts = token.split(".")
    if len(parts) != 3:
        return None
    header = json.loads(b64url_decode(parts[0]))
    payload = json.loads(b64url_decode(parts[1]))
    alg = header.get("alg", "")

    # VULN: 'none' algorithm accepted — no signature required
    if alg.lower() == "none":
        return payload   # skips all verification

    if alg == "HS256":
        expected = base64.urlsafe_b64encode(
            hmac.new(SECRET.encode(), f"{parts[0]}.{parts[1]}".encode(), hashlib.sha256).digest()
        ).rstrip(b"=").decode()
        if hmac.compare_digest(expected, parts[2]):
            return payload
    return None

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): return jsonify({"error":"No token"}),401
    payload = verify_jwt(auth[7:])
    if payload and payload.get("sub") == "administrator":
        return jsonify({"message":"Welcome admin","secret":"FLAG-abc123"})
    return jsonify({"error":"Forbidden"}),403

if __name__ == "__main__":
    app.run(debug=True)
