# ============================================================
# FIXED CODE — Basic Origin Reflection
# ============================================================
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

# ✅ FIX 1: Explicit whitelist — only exact trusted origins
ALLOWED_ORIGINS = {
    'https://trusted-app.com',
    'https://admin.trusted-app.com'
}

@app.route('/accountDetails')
def account_details():
    origin  = request.headers.get('Origin')
    session = request.cookies.get('sessionid')
    user    = USERS.get(session)

    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    response = make_response(jsonify({
        'username': user['username'],
        'apiKey':   user['apiKey'],
        'email':    user['email']
    }))

    # ✅ FIX 2: Only allow if origin is in the whitelist
    if origin and origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin']      = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        # ✅ FIX 3: Vary header prevents cache poisoning
        response.headers['Vary'] = 'Origin'

    return response
