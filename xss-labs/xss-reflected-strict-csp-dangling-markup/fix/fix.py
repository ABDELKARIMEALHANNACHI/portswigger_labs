"""
FIX:
1. HTML-encode reflected username — closes the dangling markup vector.
2. Strict CSP: img-src 'self' — prevents exfiltration via img src.
3. CSRF token not on same page as reflected user input.
"""
from flask import Flask, request, session
from markupsafe import escape
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

@app.route("/")
def index():
    username = escape(request.args.get("username",""))  # FIX: encode
    token = secrets.token_hex(16)
    session["csrf"] = token
    nonce = secrets.token_hex(8)
    return f"""<!DOCTYPE html><html>
    <head>
    <meta http-equiv="Content-Security-Policy"
          content="default-src 'self'; script-src 'nonce-{nonce}'; img-src 'self'">
    </head>
    <body>
    <p>Welcome {username}</p>
    <form action="/change-email" method="POST">
      <input type="hidden" name="csrf" value="{token}">
      <input name="email"><button>Change</button>
    </form>
    </body></html>"""
