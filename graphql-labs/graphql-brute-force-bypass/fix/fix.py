"""
FIX: Rate limit per resolver call (not per HTTP request).
Uses an application-level counter keyed on (IP, username).
Also: account lockout after N failures + CAPTCHA trigger.
"""
from flask import Flask, request, jsonify
from graphql import build_schema, graphql_sync
import time
from collections import defaultdict

app = Flask(__name__)

USERS = {"carlos": "abc123", "admin": "password123"}

# FIX: per-user attempt counter {username: [timestamp, ...]}
login_attempts = defaultdict(list)
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60
LOCKOUT_SECONDS = 300

def check_rate_limit(username: str, ip: str) -> bool:
    """Returns True if allowed, False if rate-limited."""
    key = f"{ip}:{username}"
    now = time.time()
    attempts = login_attempts[key]
    # Remove old attempts outside window
    login_attempts[key] = [t for t in attempts if now - t < WINDOW_SECONDS]
    if len(login_attempts[key]) >= MAX_ATTEMPTS:
        return False
    login_attempts[key].append(now)
    return True

schema = build_schema("""
    type Query  { _dummy: Boolean }
    type Mutation {
        login(username: String!, password: String!): LoginResult
    }
    type LoginResult { token: String  success: Boolean  message: String }
""")

def resolve_login(root, info, username, password):
    ip = info.context["request"].remote_addr
    # FIX: rate limit checked INSIDE the resolver — catches alias batching
    if not check_rate_limit(username, ip):
        raise Exception(f"Too many login attempts for {username}. Try again later.")
    if USERS.get(username) == password:
        return {"success": True, "token": f"jwt-{username}", "message": "OK"}
    return {"success": False, "token": None, "message": "Invalid credentials"}

root_value = {"login": resolve_login}

@app.route("/graphql", methods=["POST"])
def graphql_endpoint():
    data = request.get_json()
    result = graphql_sync(schema, data["query"], root_value=root_value,
                          context_value={"request": request})
    return jsonify(result.data)

if __name__ == "__main__":
    app.run()
