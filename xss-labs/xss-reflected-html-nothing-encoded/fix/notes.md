# Fix Notes — Reflected XSS HTML Context

## Root Cause
User input concatenated directly into HTML response without encoding.

## Fix
HTML-encode all reflected data: `<` → `&lt;`, `>` → `&gt;`, `"` → `&quot;`

## Semgrep Rule
```yaml
rules:
  - id: reflected-xss-python
    patterns:
      - pattern: return f"...$INPUT..."
      - pattern-not: return f"...{escape($INPUT)}..."
    message: "Potential reflected XSS: user input not HTML-encoded before reflection"
    languages: [python]
    severity: ERROR
```
