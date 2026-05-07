"""
VULNERABLE: GraphQL endpoint mounted at non-standard path.
No auth on introspection. Universal query {__typename} confirms GraphQL.
"""
from flask import Flask, request, jsonify
from graphql import build_schema, graphql_sync

app = Flask(__name__)

schema = build_schema("""
    type Query {
        getUser(id: Int!): User
        listUsers: [User]
    }
    type Mutation {
        deleteUser(id: Int!): Boolean
        changeEmail(id: Int!, email: String!): User
    }
    type User {
        id: Int
        username: String
        email: String
        isAdmin: Boolean
    }
""")

USERS = {1: {"id":1,"username":"admin","email":"admin@corp.com","isAdmin":True}}

def resolve_get_user(root, info, id): return USERS.get(id)
def resolve_list_users(root, info): return list(USERS.values())
def resolve_delete_user(root, info, id): return USERS.pop(id, None) is not None
def resolve_change_email(root, info, id, email):
    if id in USERS:
        USERS[id]["email"] = email
        return USERS[id]

root_value = {
    "getUser": resolve_get_user,
    "listUsers": resolve_list_users,
    "deleteUser": resolve_delete_user,
    "changeEmail": resolve_change_email,
}

# VULN: non-standard endpoint path — security through obscurity only
@app.route("/api/internal/graphql-dev", methods=["GET","POST"])
def graphql_endpoint():
    query = (request.get_json() or {}).get("query") or request.args.get("query","")
    result = graphql_sync(schema, query, root_value=root_value)
    return jsonify(result.data)

if __name__ == "__main__":
    app.run(debug=True)
