# Fix Notes — JS String Context XSS

## Root Cause
HTML-encoding alone is insufficient inside a JavaScript string context.
`'` must be JS-escaped as `\'` or the value JSON-encoded.

## Fix
Use `json.dumps(value)` (Python) or `Encode.forJavaScript(value)` (Java).
This produces a properly delimited, escaped JS string.

## Semgrep Rule
```yaml
rules:
  - id: xss-js-string-context
    pattern: f"... = '{$VAR}'; ..."
    message: "XSS: user input inside JS string — use json.dumps() for safe encoding"
    languages: [python]
    severity: ERROR
```
