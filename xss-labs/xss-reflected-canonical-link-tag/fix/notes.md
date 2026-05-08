# Fix — Canonical Link Tag XSS

## Root Cause
Full query string (including user-controlled params) reflected raw into
the href attribute of a <link> tag. Injecting `'` closes the href and
allows additional attributes (accesskey, onclick) to be injected.

## Fix
1. Only reflect the path, not arbitrary query parameters, into canonical URLs.
2. HTML-attribute-encode the value.
3. Validate the canonical URL against an allowlist of known paths.
