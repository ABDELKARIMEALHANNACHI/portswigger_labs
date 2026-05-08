"""
VULNERABLE: Input reflected inside a JS string. < > encoded, but not ' or \
Attacker closes the string with single quote and injects JS.
"""
from flask import Flask, request

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("search", "")
    safe = query.replace("<","&lt;").replace(">","&gt;")  # only HTML encoding
    # VULN: input inside JS string — ' not escaped
    return f"""<html><body>
    <script>var searchQuery = '{safe}'; console.log(searchQuery);</script>
    </body></html>"""
