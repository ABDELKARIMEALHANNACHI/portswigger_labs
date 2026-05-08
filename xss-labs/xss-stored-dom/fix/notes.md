# Fix — Stored DOM XSS

## Root Cause
Server replaces < with &lt; but innerHTML DECODES HTML entities.
The "encoding" is immediately undone by the sink.

## Fix
Use `textContent` instead of `innerHTML` for plain text.
If HTML is needed: `DOMPurify.sanitize(c.body)` before `innerHTML`.
