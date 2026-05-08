# Fix Notes — Attribute Context XSS

## Root Cause
Only < > encoded. Inside an attribute, the attacker breaks out using `"`.

## Fix
Full HTML attribute encoding: `"` → `&quot;`, `'` → `&#x27;`
Use OWASP Java Encoder: `Encode.forHtmlAttribute(value)`

## Semgrep Rule
```yaml
rules:
  - id: xss-incomplete-encoding-attribute
    pattern: f'... value="{$VAR}"'
    pattern-not: f'... value="{escape($VAR)}"'
    message: "XSS: user input in HTML attribute without full attribute encoding"
    languages: [python]
    severity: ERROR
```
