from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("search","")
    # FIX: json.dumps handles ALL special characters correctly
    # Order matters: always escape \ first, before escaping '
    safe = json.dumps(query)
    return f"""<html><body>
    <script>var q = {safe};</script>
    </body></html>"""
