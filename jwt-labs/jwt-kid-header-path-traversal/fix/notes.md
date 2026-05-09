# Fix Notes — kid Path Traversal

## Root Cause
`kid` used to construct a file system path: `KEYS_DIR + kid`.
Attacker sets `kid=../../dev/null` → reads empty file → signs with empty secret.

## Fix
1. Never use kid as a file path.
2. Use an in-memory key map: `keys[kid]` — path traversal impossible.
3. Validate kid against strict allowlist (alphanumeric + hyphens only).
4. If filesystem lookup unavoidable: canonicalize path + verify it stays under KEYS_DIR.

## Semgrep Rule
```yaml
rules:
  - id: jwt-kid-path-construction
    pattern: os.path.join($DIR, $KID)
    message: "JWT kid used in file path construction — path traversal risk"
    languages: [python]
    severity: ERROR
```
