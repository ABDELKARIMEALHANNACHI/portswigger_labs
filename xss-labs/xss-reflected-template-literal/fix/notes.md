# Fix — Template Literal XSS

## Root Cause
Inside JS template literals, `${...}` evaluates as an expression.
None of the standard XSS escapes (', ", <, >) prevent `${alert(1)}`.

## Fix
1. Never insert user data directly into template literals.
2. Use `json.dumps()` to produce a safe JS string value.
3. Use string concatenation with the encoded value, not template literal.

## Semgrep Rule
```yaml
rules:
  - id: xss-template-literal
    pattern: "`...${ $INPUT }...`"
    message: "XSS: user input in JS template literal — use json.dumps() instead"
    languages: [javascript]
    severity: ERROR
```
