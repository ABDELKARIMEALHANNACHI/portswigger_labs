# QUICK BURP TESTING CHECKLIST

[ ] Remove CSRF token
[ ] Switch POST → GET
[ ] Use garbage token
[ ] Use token from another session
[ ] Remove Referer
[ ] Referer query-string bypass
[ ] Check SameSite
[ ] Test _method override
[ ] Hunt sibling-domain XSS
[ ] Look for OAuth/session refresh
[ ] Find client-side redirects
