"""
VULNERABLE: < > " encoded, ' escaped to \' — but not \\ escaped.
Attacker injects \' which the encoding turns into \\' — escaping the escape!
"""
from flask import Flask, request
import html

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("search","")
    # HTML-encodes < > " — and escapes '
    safe = html.escape(query).replace("'", "\\'")
    # VULN: if user sends \' → html.escape gives \' → replace adds \ → \\'
    # But if user sends \  → html.escape gives \  → replace gives \'  → breaks escape
    return f"""<html><body>
    <script>var q = '{safe}';</script>
    </body></html>"""
