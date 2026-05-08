"""
VULNERABLE: Strict CSP blocks script execution — but dangling markup
allows exfiltration of CSRF token via unclosed attribute + img src.
CSP script-src 'self' nonce-based — but form action can be changed!
"""
from flask import Flask, request, redirect, session
import secrets

app = Flask(__name__)
app.secret_key = "dev-secret"

@app.route("/")
def index():
    username = request.args.get("username","")
    token = secrets.token_hex(16)
    session["csrf"] = token
    nonce = secrets.token_hex(8)
    # VULN: username reflected in page that also contains CSRF token
    # CSP blocks JS but dangling markup can steal the CSRF token
    return f"""<!DOCTYPE html><html>
    <head>
    <meta http-equiv="Content-Security-Policy"
          content="default-src 'self'; script-src 'nonce-{nonce}'; img-src *">
    </head>
    <body>
    <p>Welcome {username}</p>
    <form action="/change-email" method="POST">
      <input type="hidden" name="csrf" value="{token}">
      <input name="email"><button>Change</button>
    </form>
    </body></html>"""
