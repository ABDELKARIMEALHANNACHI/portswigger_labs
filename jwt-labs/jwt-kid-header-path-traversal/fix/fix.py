"""
FIX:
1. kid validated against allowlist — no filesystem lookup at all.
2. Keys stored in memory dict keyed by ID — no file path construction.
"""
import jwt
from flask import Flask, request, jsonify

app = Flask(__name__)

# FIX: keys stored in memory — kid is just a dict key, no file I/O
SIGNING_KEYS = {
    "key-2024-01": b"super-random-256-bit-secret-value-here-abc123",
    "key-2024-02": b"another-random-256-bit-secret-value-xyz789def",
}

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): return jsonify({"error":"No token"}),401
    token = auth[7:]
    try:
        # FIX: get kid for key selection
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        # FIX: kid looked up in dict — no path traversal possible
        key = SIGNING_KEYS.get(kid)
        if not key:
            raise ValueError(f"Unknown kid: {kid}")
        payload = jwt.decode(token, key, algorithms=["HS256"])
    except Exception as e:
        return jsonify({"error":str(e)}),401
    if payload.get("sub") == "administrator":
        return jsonify({"message":"Welcome admin"})
    return jsonify({"error":"Forbidden"}),403
