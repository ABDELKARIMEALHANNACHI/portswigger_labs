# MASTER CSRF DEFENSE REFERENCE

## Tier 1 — CSRF Tokens

Primary defense.

### Synchronizer Token Pattern

- token = HMAC(session_id, secret)
- stored per session
- validated server-side
- fail closed

### Signed Double Submit

Secure:
cookie = HMAC(session, secret)
form = same value

Insecure:
cookie = X
form = X

---

## Tier 2 — SameSite

Strict:
- strongest
- blocks all cross-site cookies

Lax:
- allows top-level GET

None:
- cross-site allowed
- requires Secure

---

## Tier 3 — Origin / Referer

- exact hostname matching
- never substring checks
- fail closed

---

## Tier 4 — Supporting Controls

- POST only
- disable method override
- CSP
- fix XSS
