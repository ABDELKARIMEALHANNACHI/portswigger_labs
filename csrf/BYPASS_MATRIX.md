# CSRF Bypass Matrix

| Lab | Defense | Bypass |
|------|----------|---------|
| basic-csrf-no-defenses | none | auto-submit form |
| csrf-token-method-bypass | POST token only | switch to GET |
| csrf-token-presence-bypass | validate if present | remove token |
| csrf-token-not-tied-to-session | global token pool | attacker token |
| csrf-token-tied-to-cookie | csrfKey cookie | cookie injection |
| csrf-token-duplicated-cookie | double submit | inject matching cookie |
| csrf-referer-header-absent | referer optional | no-referrer |
| csrf-broken-referer-validation | substring validation | query-string bypass |
| csrf-samesite-lax-method-override | SameSite=Lax | _method=POST |
| csrf-samesite-strict-client-redirect | SameSite=Strict | same-site redirect |
| csrf-samesite-strict-sibling-domain | SameSite=Strict | sibling XSS |
| csrf-samesite-lax-cookie-refresh | SameSite=Lax | cookie refresh |
