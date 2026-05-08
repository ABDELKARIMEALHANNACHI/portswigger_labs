from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("search","")
    # FIX: json.dumps escapes all special chars including < > / ' " \
    # Also use application/json header or place in data attribute instead
    safe = json.dumps(query)
    return f"""<html><body>
    <script>var q = {safe}; doSearch(q);</script>
    </body></html>"""
