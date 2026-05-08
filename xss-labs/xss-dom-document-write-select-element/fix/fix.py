from flask import Flask
app = Flask(__name__)

@app.route("/product")
def product():
    return """<!DOCTYPE html><html><body>
    <form>
    <select id="store">
        <option value="1">Store 1</option>
    </select>
    </form>
    <script>
        var storeId = new URLSearchParams(location.search).get('storeId');
        if (storeId && /^[a-zA-Z0-9_-]+$/.test(storeId)) {
            // FIX: DOM API instead of document.write
            var opt = document.createElement('option');
            opt.value = storeId;
            opt.textContent = storeId;   // textContent — never parsed as HTML
            document.getElementById('store').appendChild(opt);
        }
    </script>
    </body></html>"""
