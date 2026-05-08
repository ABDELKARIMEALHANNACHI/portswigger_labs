# Fix — Reflected DOM XSS

## Root Cause
Server uses string concatenation instead of `json.dumps()` → user input
can break out of the JSON string and manipulate the JS expression that eval() processes.

## Fix
1. Use proper JSON serialization (`json.dumps`, `jsonify`, `JSON.stringify`).
2. Replace `eval()` with `JSON.parse()` or `response.json()`.

## Semgrep Rule
```yaml
rules:
  - id: eval-of-user-input
    pattern: eval($INPUT)
    message: "eval() with potentially user-controlled data — DOM XSS risk"
    languages: [javascript]
    severity: ERROR
```
