# Fix Notes — Unverified JWT Signature

## Root Cause
JWT parsed by splitting on `.` and base64-decoding. Signature (third part)
never passed to any verification function.

## Fix
Use a trusted JWT library with signature verification enabled by default.
Always specify the exact algorithm — never accept what the token header says.

## Semgrep Rule
```yaml
rules:
  - id: jwt-no-verify
    pattern: jwt.decode($TOKEN, options={"verify_signature": false, ...})
    message: "JWT decoded with signature verification disabled"
    languages: [python]
    severity: ERROR

  - id: jwt-manual-split
    pattern: $TOKEN.split(".")
    message: "Manual JWT parsing detected — use a verified JWT library"
    languages: [python]
    severity: WARNING
```
