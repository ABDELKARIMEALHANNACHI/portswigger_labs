from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route("/search-results")
def search_results():
    query = request.args.get("search", "")
    # FIX: use proper JSON serialization
    return jsonify({"results": query})  # json.dumps handles escaping

@app.route("/search")
def search_page():
    return """<!DOCTYPE html><html><body>
    <div id="result"></div>
    <script>
        var query = new URLSearchParams(location.search).get('search');
        fetch('/search-results?search=' + encodeURIComponent(query))
            .then(r => r.json())   // FIX: .json() not eval()
            .then(data => {
                document.getElementById('result').textContent = data.results;
            });
    </script></body></html>"""
