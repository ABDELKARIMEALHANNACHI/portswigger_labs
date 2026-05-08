# Fix — Custom Element XSS Bypass

## Root Cause
Blocklist of standard tags. Custom HTML elements (any non-standard tag name)
are valid HTML and support all event handlers including onfocus with autofocus.

## Fix
Allowlist only. Any tag not on the approved list is stripped.
