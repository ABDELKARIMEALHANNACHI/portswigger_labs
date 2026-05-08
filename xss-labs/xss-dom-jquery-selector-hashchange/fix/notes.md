# Fix Notes — jQuery Selector Hashchange

## Root Cause
`$(userInput)` in jQuery: if the string starts with `<`, jQuery treats it
as HTML and creates DOM elements — executing any event handlers.

## Fix
Validate the hash value is a safe CSS ID (alphanumeric/dash/underscore).
Never pass user input directly to `$()`.

## Semgrep Rule
```yaml
rules:
  - id: jquery-selector-sink
    pattern: $($INPUT)
    message: "jQuery selector with user-controlled input may create arbitrary DOM elements"
    languages: [javascript]
    severity: WARNING
```
