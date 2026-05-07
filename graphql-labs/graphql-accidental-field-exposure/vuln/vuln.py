"""
VULNERABLE: User type exposes password and role via introspection.
Attacker discovers hidden fields through __type query and reads them directly.
"""
from flask import Flask, request, jsonify
from graphql import build_schema, graphql_sync

app = Flask(__name__)

USERS = {
    1: {"id":1,"username":"admin","email":"admin@corp.com","password":"supersecret123","role":"ADMIN"},
    2: {"id":2,"username":"carlos","email":"carlos@corp.com","password":"hunter2","role":"USER"},
}

# VULN: password and role fields are part of the schema — introspection exposes them
schema = build_schema("""
    type Query {
        getUser(id: Int!): User
        getCurrentUser: User
    }
    type User {
        id: Int
        username: String
        email: String
        password: String   # VULN: should NEVER be in schema
        role: String       # VULN: sensitive — exposes privilege level
    }
""")

def resolve_get_user(root, info, id):
    return USERS.get(id)   # VULN: no auth, returns everything

def resolve_get_current_user(root, info):
    return USERS.get(1)    # Simulated: always returns admin for demo

root_value = {
    "getUser": resolve_get_user,
    "getCurrentUser": resolve_get_current_user,
}

@app.route("/graphql", methods=["POST"])
def graphql_endpoint():
    data = request.get_json()
    result = graphql_sync(schema, data["query"], root_value=root_value)
    return jsonify(result.data)

if __name__ == "__main__":
    app.run(debug=True)
