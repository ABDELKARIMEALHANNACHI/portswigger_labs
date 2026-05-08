# Fix — SVG XSS bypass

## Root Cause
SVG elements support JS event handlers. `<animatetransform onbegin=...>`
fires immediately on render. Most blocklists don't cover SVG animation events.

## Fix
Allowlist SVG tags AND attributes. Never allow any `on*` attributes.
Strip unknown attributes entirely.
