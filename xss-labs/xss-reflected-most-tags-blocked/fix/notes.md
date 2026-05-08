# Fix — WAF Bypass via Allowed Tags

## Root Cause
Blocklist approach. Developers block known-bad tags but miss <body>, <details>,
<marquee>, custom elements, and hundreds of event handlers.

## Fix
Allowlist: explicitly permit only the tags and attributes needed.
Use DOMPurify (client-side) or bleach/sanitize-html (server-side).

## Semgrep Rule
```yaml
rules:
  - id: blocklist-xss-filter
    pattern: re.sub(r'<(script|img|...)', '', $INPUT)
    message: "Blocklist-based XSS filter — use allowlist sanitizer instead"
    languages: [python]
    severity: WARNING
```
