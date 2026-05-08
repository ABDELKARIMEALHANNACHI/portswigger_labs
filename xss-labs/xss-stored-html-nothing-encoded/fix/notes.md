# Fix Notes — Stored XSS

## Key Principle
Encode on OUTPUT not input. Sanitizing on input loses data fidelity.
Store raw, encode when rendering.

## Semgrep Rule
```yaml
rules:
  - id: stored-xss-raw-concat
    pattern: |
      $SB.append("<p>" + $RS.getString(...) + "</p>")
    message: "Stored XSS: DB value concatenated raw into HTML without encoding"
    languages: [java]
    severity: ERROR
```
