"""
FIX:
1. Introspection disabled (production flag).
2. All mutations require authenticated session.
3. Endpoint at standard path — security through obscurity is NOT a fix.
4. Rate limiting on endpoint.
"""
from flask import Flask, request, jsonify, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from graphql import build_schema, graphql_sync
from functools import wraps

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["100/hour"])

schema = build_schema("""
    type Query { getUser(id: Int!): UserPublic }
    type Mutation { changeEmail(id: Int!, email: String!): UserPublic }
    type UserPublic { id: Int  username: String  email: String }
""")

USERS = {1: {"id":1,"username":"admin","email":"admin@corp.com"}}

def require_auth(info):
    token = info.context["request"].headers.get("Authorization","")
    if token != "Bearer valid-admin-token":
        raise Exception("Unauthorized")

def resolve_change_email(root, info, id, email):
    require_auth(info)  # FIX: auth required
    if id in USERS:
        USERS[id]["email"] = email
        return USERS[id]

root_value = {
    "getUser": lambda root, info, id: USERS.get(id),
    "changeEmail": resolve_change_email,
}

DISABLE_INTROSPECTION = True

@app.route("/graphql", methods=["POST"])
@limiter.limit("30/minute")
def graphql_endpoint():
    data = request.get_json()
    query = data.get("query","")
    # FIX: block introspection in production
    if DISABLE_INTROSPECTION and ("__schema" in query or "__type" in query):
        return jsonify({"errors":[{"message":"Introspection is disabled"}]}), 403
    result = graphql_sync(schema, query, root_value=root_value,
                          context_value={"request": request})
    return jsonify(result.data)

if __name__ == "__main__":
    app.run()
