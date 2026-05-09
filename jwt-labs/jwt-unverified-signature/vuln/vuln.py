"""
VULNERABLE: JWT decoded but signature never verified.
Server trusts whatever is in the payload — any signed (or unsigned) token accepted.
"""
import base64, json
from flask import Flask, request, jsonify

app = Flask(__name__)

def b64url_decode(s):
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)

def parse_jwt_no_verify(token):
    """VULN: decodes without EVER checking the signature."""
    parts = token.split(".")
    if len(parts) != 3:
        return None
    payload = json.loads(b64url_decode(parts[1]))
    return payload   # signature in parts[2] is NEVER checked

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "No token"}), 401
    token = auth[7:]
    payload = parse_jwt_no_verify(token)   # VULN
    if payload and payload.get("sub") == "administrator":
        return jsonify({"message": "Welcome admin", "users": ["carlos","wiener"]})
    return jsonify({"error": "Forbidden"}), 403

if __name__ == "__main__":
    app.run(debug=True)
