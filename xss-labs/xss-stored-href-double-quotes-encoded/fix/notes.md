# Fix Notes — Stored XSS href javascript: URI

## Root Cause
Only `"` encoded. `javascript:` URI scheme in href executes on click.

## Fix
1. Validate URL scheme — only allow `http:` and `https:`.
2. Use `Encode.forUriComponent()` for URL values.
3. Use `Encode.forHtmlAttribute()` for HTML attribute context.

## Semgrep Rule
```yaml
rules:
  - id: unsafe-href-assignment
    pattern: |
      $VAR = $INPUT
      ...
      href="$VAR"
    message: "Potential XSS via href — validate URL scheme (http/https only)"
    languages: [python]
    severity: WARNING
```
