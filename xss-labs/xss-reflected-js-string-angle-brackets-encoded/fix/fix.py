from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("search", "")
    # FIX: json.dumps produces a properly JS-encoded string including escaping '
    # Result: var searchQuery = "user's input" — safe JS string
    safe_js = json.dumps(query)
    return f"""<html><body>
    <script>var searchQuery = {safe_js};</script>
    </body></html>"""
