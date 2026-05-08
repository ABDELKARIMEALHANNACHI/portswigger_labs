# Fix — Dangling Markup Attack

## Root Cause
Even when XSS is blocked by CSP, unencoded reflected input creates
"dangling markup" — unclosed HTML attributes that consume subsequent page
content and exfiltrate it via allowed resource loads (img, script, link).

## Fix
1. HTML-encode ALL reflected output — prevents dangling markup.
2. Tighten CSP: `img-src 'self'` — blocks external image loads.
3. Don't reflect user-controlled values on pages with sensitive tokens.

## Semgrep Rule
```yaml
rules:
  - id: reflected-input-without-encoding
    pattern: f"...$REQ.args.get(...)..."
    pattern-not: f"...escape($REQ.args.get(...))..."
    message: "Reflected input without HTML encoding — dangling markup / XSS risk"
    languages: [python]
    severity: ERROR
```
