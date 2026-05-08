"""
VULNERABLE: Server serves page containing client-side JS that passes
location.search directly into document.write() — DOM XSS.
Server-side code is fine; the vulnerability lives in the JavaScript.
"""
from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    # VULN: the JS reads location.search and writes it raw to the DOM
    return """
    <!DOCTYPE html><html><body>
    <h1>Search</h1>
    <script>
        var query = (new URLSearchParams(window.location.search)).get('search');
        document.write('<img src="/search?q=' + query + '">');
        // VULN: document.write with unsanitized location.search
        // Payload: "><svg onload=alert(1)>
    </script>
    </body></html>
    """
if __name__ == "__main__":
    app.run(debug=True)
