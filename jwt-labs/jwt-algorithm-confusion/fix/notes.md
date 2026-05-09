# Fix Notes — Algorithm Confusion

## Root Cause
Server accepts both RS256 and HS256 on the same public key.
When a library like PyJWT receives alg=HS256 with an RSA public key,
it uses the PEM bytes as the HMAC secret — which is exactly what the
attacker uses to sign. The verification succeeds.

## Fix
Pin ONE algorithm per endpoint. NEVER pass both RS256 and HS256 together.
If RS256 is used for verification, reject any token claiming alg=HS256.

## Semgrep Rule
```yaml
rules:
  - id: jwt-multiple-algorithms
    pattern: jwt.decode($T, $K, algorithms=["RS256", "HS256", ...])
    message: "JWT algorithm confusion risk: multiple algorithms accepted"
    languages: [python]
    severity: ERROR
```
