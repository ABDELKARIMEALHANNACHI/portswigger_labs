# Fix — onclick HTML Entity Bypass

## Root Cause
Escaping JS special chars (' → \') is bypassed by HTML entities (&apos; → ')
because the HTML parser decodes entities BEFORE the JS engine processes
the attribute value.

## Fix
1. Avoid inline event handlers with user-controlled data entirely.
2. Use data attributes + addEventListener in external JS.
3. If inline onclick is unavoidable: use json.dumps() AND html.escape() in
   the correct order (json first, then html).
