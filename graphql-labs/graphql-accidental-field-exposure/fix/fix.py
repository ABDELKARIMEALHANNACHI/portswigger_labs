"""
FIX: Remove sensitive fields from schema; use separate DTO/response type.
1. Password never included in GraphQL schema.
2. Role only returned to ADMIN callers.
3. Introspection disabled in production.
"""
from flask import Flask, request, jsonify
from graphql import build_schema, graphql_sync

app = Flask(__name__)

USERS = {
    1: {"id":1,"username":"admin","email":"admin@corp.com","_password":"supersecret123","_role":"ADMIN"},
    2: {"id":2,"username":"carlos","email":"carlos@corp.com","_password":"hunter2","_role":"USER"},
}

# FIX: password REMOVED from schema. role gated behind resolver logic.
schema = build_schema("""
    type Query {
        getUser(id: Int!): UserPublic
        getCurrentUser: UserSelf
    }
    type UserPublic {
        id: Int
        username: String
    }
    type UserSelf {
        id: Int
        username: String
        email: String
    }
""")

def get_current_user(req):
    token = req.headers.get("Authorization","")
    return {"id":1,"_role":"ADMIN"} if token == "Bearer admin-token" else None

def resolve_get_user(root, info, id):
    u = USERS.get(id)
    if not u: return None
    # FIX: only expose safe public fields
    return {"id": u["id"], "username": u["username"]}

def resolve_get_current_user(root, info):
    caller = get_current_user(info.context["request"])
    if not caller: return None
    u = USERS.get(caller["id"])
    # FIX: email only to the user themselves
    return {"id": u["id"], "username": u["username"], "email": u["email"]}

root_value = {
    "getUser": resolve_get_user,
    "getCurrentUser": resolve_get_current_user,
}

@app.route("/graphql", methods=["POST"])
def graphql_endpoint():
    data = request.get_json()
    # FIX: disable introspection in non-debug mode
    if "__schema" in data.get("query","") or "__type" in data.get("query",""):
        return jsonify({"errors":[{"message":"Introspection disabled"}]}), 403
    result = graphql_sync(schema, data["query"], root_value=root_value,
                          context_value={"request": request})
    return jsonify(result.data)

if __name__ == "__main__":
    app.run()
