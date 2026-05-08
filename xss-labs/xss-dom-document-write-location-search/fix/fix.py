"""
FIX: Replace document.write with safe DOM APIs.
Encode the value before inserting into an attribute.
"""
from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return """
    <!DOCTYPE html><html><body>
    <h1>Search</h1>
    <img id="search-img" src="">
    <script>
        // FIX 1: Never use document.write with user data
        // FIX 2: Use encodeURIComponent to safely encode URL parameter
        var params = new URLSearchParams(window.location.search);
        var query = params.get('search') || '';
        // FIX 3: Set attribute via DOM API — not string concatenation
        document.getElementById('search-img')
                .setAttribute('src', '/search?q=' + encodeURIComponent(query));
    </script>
    </body></html>
    """
