# Deep Dive — Basic Origin Reflection

## How the Browser Enforces CORS (Step by Step)

```
1. JS on evil.com calls fetch('https://victim.com/data', {credentials:'include'})
2. Browser adds header:  Origin: https://evil.com
3. Request reaches server
4. Server responds with:
     Access-Control-Allow-Origin: https://evil.com    ← server decision
     Access-Control-Allow-Credentials: true
5. Browser checks: does ACAO match the request origin? YES
6. Browser: "server approved this — JS may read the response"
7. JS reads response body — attack succeeds
```

If step 4 returned NO ACAO header, step 6 would block — JS gets a CORS error and cannot read anything.

---

## Why Credentials Make It Critical

```
Scenario A — No withCredentials:
  Browser sends request without cookies
  Server treats it as anonymous user
  Response: {} or 401
  Attacker gets: nothing useful

Scenario B — withCredentials: true:
  Browser sends request WITH victim's session cookie
  Server treats it as the authenticated victim
  Response: {"apiKey":"TOP_SECRET","email":"admin@corp.com"}
  Attacker gets: full account access
```

---

## What an Attacker Does With an API Key

```
API key = password for programmatic access

With victim's API key:
  GET  /user/profile        → full PII
  GET  /billing             → card info, address
  POST /settings/email      → change email → account takeover
  POST /transfer            → move money (fintech apps)
  GET  /messages            → read all private messages
  DELETE /account           → destroy the account
```

---

## Real CVEs Using This Exact Pattern

| Target   | Impact                        |
|----------|-------------------------------|
| Shopify  | Merchant store data exposed   |
| Badoo    | Dating app user PII           |
| BitFinex | Crypto exchange ATO           |
| Uber     | Rider/driver data             |
