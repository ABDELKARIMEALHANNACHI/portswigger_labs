from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("search","")
    # FIX: json.dumps escapes backtick-unsafe chars
    # Better: avoid template literals with user data entirely
    safe = json.dumps(query)
    return f"""<html><body>
    <script>
        var userInput = {safe};   // regular string via json.dumps
        var msg = "Hello " + userInput + ", your results are ready.";
        document.getElementById('msg').textContent = msg;
    </script>
    </body></html>"""
