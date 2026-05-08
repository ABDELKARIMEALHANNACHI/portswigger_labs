# Fix Notes — jQuery href Sink

## Root Cause
jQuery `.attr('href', value)` sets the href verbatim. `javascript:` is a
valid URI scheme that browsers execute on click.

## Fix
Validate the URL scheme. Only allow `http:` or `https:`. Use `new URL()` for safe parsing.

## Semgrep Rule
```yaml
rules:
  - id: jquery-href-javascript-uri
    pattern: $EL.attr('href', $INPUT)
    message: "jQuery href sink may allow javascript: URI injection"
    languages: [javascript]
    severity: WARNING
```
