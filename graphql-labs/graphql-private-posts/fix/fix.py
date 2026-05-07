"""
FIX: Authorization check + field-level protection on getBlogPost.
1. Resolver checks isPublic flag before returning.
2. postPassword field only resolved for authenticated admins.
3. getAllPosts filters to public-only for unauthenticated callers.
"""
from flask import Flask, request, jsonify, g
from graphql import build_schema, graphql_sync
from functools import wraps

app = Flask(__name__)

POSTS = {
    1: {"id":1,"title":"Welcome","content":"Hello world","postPassword":None,"isPublic":True},
    2: {"id":2,"title":"Secret Draft","content":"Top secret","postPassword":"peter:Th3SecretPass!","isPublic":False},
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
        postPassword: String
        isPublic: Boolean
    }
""")

def get_current_user(req):
    token = req.headers.get("Authorization", "")
    return {"role": "admin"} if token == "Bearer admin-token" else None

def resolve_get_blog_post(root, info, id):
    post = POSTS.get(id)
    if not post:
        return None
    user = get_current_user(info.context["request"])
    # FIX: only return private posts to admins
    if not post["isPublic"] and (not user or user["role"] != "admin"):
        return None
    # FIX: strip postPassword unless admin
    if not user or user["role"] != "admin":
        return {**post, "postPassword": None}
    return post

def resolve_get_all_posts(root, info):
    user = get_current_user(info.context["request"])
    posts = list(POSTS.values())
    if not user or user["role"] != "admin":
        posts = [p for p in posts if p["isPublic"]]
    return [{**p, "postPassword": None} if (not user or user["role"]!="admin") else p
            for p in posts]

root_value = {
    "getBlogPost": resolve_get_blog_post,
    "getAllPosts": resolve_get_all_posts,
}

@app.route("/graphql", methods=["POST"])
def graphql_endpoint():
    data = request.get_json()
    result = graphql_sync(schema, data["query"], root_value=root_value,
                          variable_values=data.get("variables"),
                          context_value={"request": request})
    return jsonify(result.data)

if __name__ == "__main__":
    app.run()
