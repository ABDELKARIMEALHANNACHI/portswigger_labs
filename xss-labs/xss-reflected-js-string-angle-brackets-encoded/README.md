# Lab 9 — Reflected XSS in JS String, Angle Brackets Encoded (APPRENTICE)

## Payload
```
/search?search='-alert(1)-'
```
Closes the JS string, executes alert, reopens string to avoid syntax error.
