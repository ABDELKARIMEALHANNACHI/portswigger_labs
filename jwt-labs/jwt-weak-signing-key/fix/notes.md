# Fix Notes — Weak JWT Signing Key

## Root Cause
HS256 JWT signed with a short, common string ("secret", "password", etc.)
that exists in password wordlists. hashcat mode 16500 cracks HS256 JWTs.

## Fix
1. Use cryptographically random secret: `secrets.token_hex(32)` (256 bits).
2. Never hardcode the secret in source code.
3. Load from environment variable or secrets manager (Vault, AWS SSM, etc.).
4. Prefer asymmetric algorithms (RS256, ES256) — private key stays on server.

## Semgrep Rule
```yaml
rules:
  - id: jwt-hardcoded-secret
    patterns:
      - pattern: jwt.encode($PAYLOAD, "$SECRET", ...)
      - pattern-not: jwt.encode($PAYLOAD, os.environ.get(...), ...)
    message: "JWT signed with hardcoded secret — use environment variable"
    languages: [python]
    severity: ERROR
```
