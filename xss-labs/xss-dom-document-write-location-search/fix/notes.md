# Fix Notes — DOM XSS document.write

## Root Cause
`document.write()` treats its argument as raw HTML. Any user-controlled
data flowing into it creates an XSS sink.

## Fix
1. Replace `document.write` with `textContent`, `setAttribute`, or DOM APIs.
2. Use `encodeURIComponent()` for URL context.
3. Use `DOMPurify.sanitize()` if HTML output is required.

## Semgrep Rule
```yaml
rules:
  - id: dom-xss-document-write
    patterns:
      - pattern: document.write(... + $INPUT + ...)
      - pattern-not: document.write(... + encodeURIComponent($INPUT) + ...)
    message: "DOM XSS: document.write with potentially tainted input"
    languages: [javascript]
    severity: ERROR
```
