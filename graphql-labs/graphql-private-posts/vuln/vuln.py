"""
VULNERABLE: GraphQL resolver — no authorization on getBlogPost.
The resolver fetches ANY post by ID regardless of isPublic flag.
"""
from flask import Flask, request, jsonify
from graphql import build_schema, graphql_sync

app = Flask(__name__)

POSTS = {
    1: {"id": 1, "title": "Welcome", "content": "Hello world", "isPublic": True},
    2: {"id": 2, "title": "Secret Draft", "content": "Top secret content here",
        "postPassword": "peter:Th3SecretPass!", "isPublic": False},
}

schema = build_schema("""
    type Query {
        getBlogPost(id: Int!): BlogPost
        getAllPosts: [BlogPost]
    }
    type BlogPost {
        id: Int
        title: String
        content: String
        postPassword: String   # ← sensitive field returned to anyone
        isPublic: Boolean
    }
""")

def resolve_get_blog_post(root, info, id):
    # VULN: no auth check, no isPublic filter
    return POSTS.get(id)

def resolve_get_all_posts(root, info):
    # VULN: returns ALL posts including private ones
    return list(POSTS.values())

root_value = {
    "getBlogPost": resolve_get_blog_post,
    "getAllPosts": resolve_get_all_posts,
}

@app.route("/graphql", methods=["GET", "POST"])
def graphql_endpoint():
    data = request.get_json()
    result = graphql_sync(schema, data["query"], root_value=root_value,
                          variable_values=data.get("variables"))
    return jsonify(result.data)

if __name__ == "__main__":
    app.run(debug=True)
