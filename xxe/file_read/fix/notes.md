# Fix Notes — XML External Entity XXE — file_read

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
  - id: detect-file_read
    message: "Potential XML External Entity XXE — file_read vulnerability"
    severity: ERROR
    languages: [python, java]
    patterns:
      - pattern: |
          # add detection pattern here
```
