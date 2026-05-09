# Fix Notes — JWK Header Injection

## Root Cause
Server fetches the verification key from the token's own `jwk` header parameter.
Attacker generates a key pair, embeds the public key in the token, signs with
the private key → server verifies with attacker's own public key → trusts it.

## Fix
1. NEVER use keys from the token header for verification.
2. Maintain a server-side list of trusted public keys.
3. If using a JWKS endpoint, pin the URL at configuration time.

## Semgrep Rule
```yaml
rules:
  - id: jwt-jwk-header-used
    pattern: header.getJWK()
    message: "JWT verification key sourced from token header — jwk injection risk"
    languages: [java]
    severity: ERROR
```
