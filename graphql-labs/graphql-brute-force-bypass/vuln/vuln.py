"""
VULNERABLE: Login mutation with per-IP rate limit.
Rate limit checks HTTP request count — alias batching sends
100 login attempts in a single HTTP request, bypassing the limit.
"""
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from graphql import build_schema, graphql_sync

app = Flask(__name__)
# VULN: rate limit is per HTTP request, not per login attempt
limiter = Limiter(get_remote_address, app=app)

USERS = {"carlos": "abc123", "admin": "password123"}

schema = build_schema("""
    type Query  { _dummy: Boolean }
    type Mutation {
        login(username: String!, password: String!): LoginResult
    }
    type LoginResult { token: String  success: Boolean  message: String }
""")

def resolve_login(root, info, username, password):
    if USERS.get(username) == password:
        return {"success": True, "token": f"jwt-token-for-{username}", "message": "Login successful"}
    return {"success": False, "token": None, "message": "Invalid credentials"}

root_value = {"login": resolve_login}

@app.route("/graphql", methods=["POST"])
@limiter.limit("5/minute")   # VULN: 5 HTTP requests/min — alias batching evades this
def graphql_endpoint():
    data = request.get_json()
    result = graphql_sync(schema, data["query"], root_value=root_value)
    return jsonify(result.data)

if __name__ == "__main__":
    app.run(debug=True)
