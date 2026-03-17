# Fix Notes — Server-Side Template Injection SSTI — jinja2

## Root Cause
<!-- What was the exact developer mistake? -->

## Fix Applied
<!-- What changed and why -->

## Secure Pattern
```python
# paste secure code here
```

## Semgrep Detection Rule
```yaml
rules:
  - id: detect-jinja2
    message: "Potential Server-Side Template Injection SSTI — jinja2 vulnerability"
    severity: ERROR
    languages: [python, java]
    patterns:
      - pattern: |
          # add detection pattern here
```
