"""
VULNERABLE: document.write used to build a <select> dropdown from location.search.
Injecting </select> breaks out of the select element context.
"""
from flask import Flask
app = Flask(__name__)

@app.route("/product")
def product():
    return """<!DOCTYPE html><html><body>
    <form>
    <select id="store">
    <script>
        var store = new URLSearchParams(location.search).get('storeId');
        // VULN: document.write inside select — inject </select> to escape
        document.write('<option value=1>Store 1</option>');
        if (store) {
            document.write('<option value="' + store + '">' + store + '</option>');
        }
    </script>
    </select>
    </form></body></html>"""
