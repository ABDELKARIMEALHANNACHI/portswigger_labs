# ============================================================
# VULNERABLE CODE — Trusted Insecure Protocols
# DO NOT USE IN PRODUCTION
# ============================================================
import re
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

# ❌ VULNERABILITY 1: Regex trusts ALL subdomains over HTTP AND HTTPS
# https? means both protocols are accepted — HTTP subdomain = MITM target
ORIGIN_REGEX = re.compile(
    r'^https?://([a-z0-9-]+\.)?lab-id\.web-security-academy\.net$'
#    ^^^^^^^^
#    http OR https — this is the critical mistake
)

@app.route('/accountDetails')
def account_details():
    origin  = request.headers.get('Origin', '')
    session = request.cookies.get('sessionid')
    user    = USERS.get(session)

    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    response = make_response(jsonify({
        'username': user['username'],
        'apiKey':   user['apiKey'],
        'email':    user['email']
    }))

    if origin and ORIGIN_REGEX.match(origin):
        response.headers['Access-Control-Allow-Origin']      = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Vary'] = 'Origin'

    return response


# ❌ VULNERABILITY 2: Reflected XSS on stock subdomain
# Runs on http://stock.lab-id.web-security-academy.net
@app.route('/stock')
def stock_check():
    product_id = request.args.get('productId', '')
    store_id   = request.args.get('storeId', '')

    # ❌ product_id injected into HTML with no sanitization → reflected XSS
    return f"""
    <html><body>
      <h1>Stock Check</h1>
      <p>Product: {product_id}</p>
    </body></html>
    """
    # if productId = 4<script>malicious_cors_payload</script>
    # → script executes in context of stock subdomain
    # → CORS request carries trusted Origin: http://stock.lab-id...
    # → main server approves it → attacker reads victim's API key

if __name__ == '__main__':
    app.run(port=8080)
