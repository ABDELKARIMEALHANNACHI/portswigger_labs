# Fix Notes — jku Header Injection

## Root Cause
Server makes an outbound request to the URL from the token's `jku` parameter.
This is also an SSRF vector — jku can point to internal services.

## Fix
1. NEVER read jku from the token — pin JWKS URL in server config.
2. If JWKS must be dynamic, maintain a strict allowlist of trusted URLs.
3. Validate `kid` against pre-loaded trusted key IDs.
4. Block outbound requests from JWT verification code to arbitrary URLs.

## Semgrep Rule
```yaml
rules:
  - id: jwt-jku-from-token
    pattern: |
      $JKU = $HEADER.get("jku")
      ...
      requests.get($JKU, ...)
    message: "SSRF + JWT key injection: jku URL fetched from token header"
    languages: [python]
    severity: ERROR
```
