"""
VULNERABLE: GraphQL mutation via GET or x-www-form-urlencoded.
No CSRF token. SameSite=None cookies. Classic CSRF attack vector.
"""
from flask import Flask, request, jsonify, make_response
from graphql import build_schema, graphql_sync

app = Flask(__name__)

USERS = {1: {"id":1,"username":"admin","email":"admin@corp.com"}}

schema = build_schema("""
    type Query  { getUser(id: Int!): User }
    type Mutation {
        changeEmail(email: String!): User
        deleteAccount: Boolean
    }
    type User { id: Int  username: String  email: String }
""")

def resolve_change_email(root, info, email):
    # Simulates: update based on session cookie
    USERS[1]["email"] = email
    return USERS[1]

def resolve_delete_account(root, info):
    USERS.clear()
    return True

root_value = {
    "getUser": lambda r, i, id: USERS.get(id),
    "changeEmail": resolve_change_email,
    "deleteAccount": resolve_delete_account,
}

@app.route("/graphql", methods=["GET","POST"])   # VULN: GET allowed
def graphql_endpoint():
    # VULN: accepts x-www-form-urlencoded — browser form can submit this
    if request.content_type and "application/x-www-form-urlencoded" in request.content_type:
        query = request.form.get("query","")
    elif request.content_type and "application/json" in request.content_type:
        query = (request.get_json() or {}).get("query","")
    else:
        query = request.args.get("query","")  # VULN: GET param

    result = graphql_sync(schema, query, root_value=root_value)
    resp = make_response(jsonify(result.data))
    # VULN: SameSite=None allows cross-site cookie sending
    resp.set_cookie("session", "user-session-token", samesite="None", secure=True)
    return resp

if __name__ == "__main__":
    app.run(debug=True)
