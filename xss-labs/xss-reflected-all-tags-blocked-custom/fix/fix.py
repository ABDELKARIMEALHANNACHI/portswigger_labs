"""
FIX: Allowlist — only permit explicitly approved tags.
Custom elements are not in the allowlist → stripped.
"""
from flask import Flask, request
import bleach

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("search", "")
    clean = bleach.clean(query, tags=["b","i","em","strong"], attributes={}, strip=True)
    return f"<html><body><p>{clean}</p></body></html>"
