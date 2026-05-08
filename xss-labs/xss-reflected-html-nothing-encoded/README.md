# Lab 1 — Reflected XSS HTML Context, Nothing Encoded (APPRENTICE)

## Payload
```
/search?search=<script>alert(1)</script>
```

## Root Cause
No output encoding. User input concatenated raw into HTML response.

## Fix
`escape(user_input)` before reflection. Use templating engine auto-escape.
