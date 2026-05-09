# Fix Notes — alg:none Attack

## Root Cause
Server reads the `alg` field from the token's own header and uses it to
decide how to verify. If `alg=none`, it skips verification entirely.

## Fix
NEVER trust the algorithm specified in the token header.
Always hardcode the expected algorithm in your verification call.
Most modern JWT libraries reject 'none' by default — but you must still
provide an explicit allowlist.

## Semgrep Rule
```yaml
rules:
  - id: jwt-algorithm-none-allowed
    pattern: jwt.decode($T, $K, algorithms=[..., "none", ...])
    message: "JWT verification allows 'none' algorithm — authentication bypass"
    languages: [python]
    severity: ERROR

  - id: jwt-no-algorithms-param
    pattern: jwt.decode($T, $K)
    pattern-not: jwt.decode($T, $K, algorithms=...)
    message: "JWT decode missing explicit algorithms parameter"
    languages: [python]
    severity: ERROR
```
