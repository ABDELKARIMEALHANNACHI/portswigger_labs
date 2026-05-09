"""
FIX: Always verify JWT signature using PyJWT with explicit algorithm.
"""
import jwt   # pip install PyJWT
from flask import Flask, request, jsonify

app = Flask(__name__)

PUBLIC_KEY = open("public.pem").read()   # RSA public key

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "No token"}), 401
    token = auth[7:]
    try:
        # FIX: verify=True (default), explicit algorithms list
        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"],   # FIX: explicit — never allow 'none' or ['RS256','HS256']
            options={"verify_exp": True}
        )
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"error": f"Invalid token: {e}"}), 401

    if payload.get("sub") == "administrator":
        return jsonify({"message": "Welcome admin"})
    return jsonify({"error": "Forbidden"}), 403
