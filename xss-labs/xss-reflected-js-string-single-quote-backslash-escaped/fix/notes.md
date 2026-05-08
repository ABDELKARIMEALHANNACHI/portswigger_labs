# Fix — JS String Escape Bypass via </script>

## Root Cause
The HTML parser processes </script> BEFORE the JS engine evaluates the string.
Escaping ' and \ is irrelevant — the script block terminates at </script>.

## Fix
1. Use `json.dumps()` which escapes `<` as `\u003c` and `/` as `\/`.
2. Or use `Encode.forJavaScript()` from OWASP Java Encoder.
3. Consider using data attributes + JS to avoid inline JS entirely.
