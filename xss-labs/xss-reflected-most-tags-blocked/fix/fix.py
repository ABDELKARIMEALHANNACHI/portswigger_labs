"""
FIX: Allowlist approach — only permit known-safe tags and attributes.
Blocklists always have gaps. Use a proper HTML sanitizer (bleach, DOMPurify).
"""
from flask import Flask, request
import bleach  # pip install bleach

app = Flask(__name__)

ALLOWED_TAGS = ["p", "b", "i", "em", "strong", "a"]
ALLOWED_ATTRS = {"a": ["href"]}

@app.route("/search")
def search():
    query = request.args.get("search","")
    # FIX: allowlist-based sanitization via bleach
    clean = bleach.clean(query, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
    return f"<html><body><p>{clean}</p></body></html>"
