# Fix — Escape Sequence Bypass (\\ before \')

## Root Cause
Manual escaping applied in wrong order. Backslash itself was not escaped
before the single-quote escape — allowing `\'` to become `\\'` in the
output, which the JS engine interprets as escaped backslash + string end.

## Fix
Use `json.dumps()` — it handles escaping in the correct order automatically.
