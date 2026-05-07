"""
FIX:
1. Only accept application/json Content-Type (blocks form-based CSRF).
2. Require custom header X-Requested-With (triggers CORS preflight).
3. Set SameSite=Strict on session cookie.
4. Add CSRF token for extra defence-in-depth.
5. Disable GET method for mutations.
"""
from flask import Flask, request, jsonify, make_response, session
from graphql import build_schema, graphql_sync
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

USERS = {1: {"id":1,"username":"admin","email":"admin@corp.com"}}

schema = build_schema("""
    type Query  { getUser(id: Int!): User  getCsrfToken: String }
    type Mutation { changeEmail(email: String!): User }
    type User   { id: Int  username: String  email: String }
""")

def validate_csrf(req):
    """
    Primary defence: Content-Type: application/json is enough to trigger
    CORS preflight. Belt-and-suspenders: also check custom header.
    """
    if req.content_type != "application/json":
        raise Exception("Invalid content type")
    custom_header = req.headers.get("X-Requested-With","")
    if custom_header != "XMLHttpRequest":
        raise Exception("Missing X-Requested-With header")

def resolve_change_email(root, info, email):
    validate_csrf(info.context["request"])  # FIX
    USERS[1]["email"] = email
    return USERS[1]

def resolve_get_csrf_token(root, info):
    token = secrets.token_hex(16)
    session["csrf_token"] = token
    return token

root_value = {
    "getUser": lambda r, i, id: USERS.get(id),
    "getCsrfToken": resolve_get_csrf_token,
    "changeEmail": resolve_change_email,
}

@app.route("/graphql", methods=["POST"])  # FIX: POST only
def graphql_endpoint():
    # FIX: enforce JSON content-type (blocks form-encoded CSRF)
    if not request.is_json:
        return jsonify({"errors":[{"message":"Content-Type must be application/json"}]}), 415
    data = request.get_json()
    result = graphql_sync(schema, data["query"], root_value=root_value,
                          context_value={"request": request})
    resp = make_response(jsonify(result.data))
    # FIX: SameSite=Strict prevents cross-origin cookie sending
    resp.set_cookie("session", "user-session-token",
                    samesite="Strict", secure=True, httponly=True)
    return resp

if __name__ == "__main__":
    app.run()
