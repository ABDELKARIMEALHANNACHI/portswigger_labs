# Fix Notes — DOM XSS innerHTML

## Fix
Replace `element.innerHTML = userInput` with `element.textContent = userInput`.
`textContent` never parses content as HTML.

If HTML output is required: `element.innerHTML = DOMPurify.sanitize(userInput)`

## Semgrep Rule
```yaml
rules:
  - id: dom-xss-innerhtml
    pattern: $EL.innerHTML = $INPUT
    pattern-not: $EL.innerHTML = DOMPurify.sanitize($INPUT)
    message: "DOM XSS: innerHTML assignment without DOMPurify sanitization"
    languages: [javascript]
    severity: ERROR
```
