# Fix — DOM XSS document.write select element

## Fix
Use `createElement` + `textContent` instead of `document.write`.
Validate storeId against an allowlist or alphanumeric pattern.
