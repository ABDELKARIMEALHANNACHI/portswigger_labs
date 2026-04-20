# ============================================================
# VULNERABLE CODE — Basic Origin Reflection
# DO NOT USE IN PRODUCTION
# ============================================================
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

# Simulated user database
USERS = {
    'sessionid_admin':  {'username': 'administrator', 'apiKey': 'admin_secret_key_9x3f', 'email': 'admin@lab.net'},
    'sessionid_wiener': {'username': 'wiener',        'apiKey': 'wiener_key_7g2k',       'email': 'wiener@lab.net'},
}

# ❌ VULNERABLE endpoint — mirrors any origin blindly
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

    # ❌ VULNERABILITY HERE:
    # No validation — any origin is reflected back.
    # Any website can read this authenticated response
    # using the victim's session cookie.
    if origin:
        response.headers['Access-Control-Allow-Origin']      = origin  # ← blind mirror
        response.headers['Access-Control-Allow-Credentials'] = 'true'  # ← allows cookies

    return response

if __name__ == '__main__':
    app.run(port=8080, debug=True)
