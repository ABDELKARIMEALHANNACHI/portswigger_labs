"""
VULNERABLE: Server reflects JSON response; client-side JS evals it → DOM XSS.
The server returns user input in JSON; JS uses eval() to parse it.
"""
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/search")
def search_page():
    return """<!DOCTYPE html><html><body>
    <div id="result"></div>
    <script>
        var query = new URLSearchParams(location.search).get('search');
        // Fetches /search-results?search=QUERY and eval()s the JSON response
        fetch('/search-results?search=' + query)
            .then(r => r.text())
            .then(data => {
                // VULN: eval() on server response containing user input
                eval('var result = ' + data);
                document.getElementById('result').textContent = result.results;
            });
    </script></body></html>"""

@app.route("/search-results")
def search_results():
    query = request.args.get("search", "")
    # VULN: raw string concat into JSON-like response — not proper JSON encoding
    return '{"results":"' + query + '"}'
