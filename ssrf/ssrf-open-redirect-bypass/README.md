# SSRF with Filter Bypass via Open Redirection

## Lab Info
- **Source**: PortSwigger Web Security Academy
- **Level**: PRACTITIONER
- **Category**: SSRF — Open Redirect Chain

---

## What This Lab Covers

This lab demonstrates how an **open redirect vulnerability** on an allowed domain
can be chained with SSRF to bypass a restrictive filter.

The stock checker has a filter that only allows requests to the **local application itself**
— it rejects any URL pointing directly to a different host.

However, the application has an **open redirect** at `/product/nextProduct?path=`
that places the `path` parameter directly into a `Location` header with no validation.

The attacker chains both:
1. The `stockApi` parameter points to the **local open redirect** (passes filter)
2. The open redirect sends a `302` to `http://192.168.0.12:8080/admin` (internal target)
3. The stock checker follows the redirect → reaches the internal admin panel

---

## Why This Vulnerability Is Interesting

The filter is **conceptually correct** — it only allows the application's own domain.
The implementation is **broken** because:
- It trusts the initial URL but does not validate redirect destinations
- The HTTP client follows `3xx` redirects by default
- The open redirect on the same trusted domain acts as a bridge to anywhere

This is the most common real-world SSRF bypass pattern.
Any open redirect on a whitelisted domain collapses the entire whitelist.

---

## Goal

Delete the user `carlos` via the internal admin interface at:
`http://192.168.0.12:8080/admin`

---

## The Two Vulnerabilities

| # | Vulnerability | Location | Effect |
|---|---|---|---|
| 1 | SSRF | `stockApi` parameter | Server fetches user-controlled URL |
| 2 | Open Redirect | `/product/nextProduct?path=` | Redirects to any user-supplied URL |

Neither alone is sufficient. Chained together: full internal access.

---

## Solution Steps

1. Visit a product page. Click **Check stock**. Intercept in Burp Suite. Send to Repeater.
2. Try `stockApi=http://192.168.0.12:8080/admin` — observe it is blocked (not local app).
3. Click **Next product** on any product page. Intercept the request.
4. Observe: `GET /product/nextProduct?path=/product?productId=2`
5. The response is `302 Location: /product?productId=2` — the `path` param goes directly into `Location`.
6. Test the open redirect: change `path` to `http://evil.com` — returns `302 Location: http://evil.com`.
7. Open redirect confirmed. Now chain it with SSRF:
8. In Repeater, set `stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin`
9. The filter passes (URL starts with local path). Server follows `302` to internal admin.
10. Admin panel HTML returned (HTTP 200). Confirm carlos is listed.
11. Change to: `stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin/delete?username=carlos`
12. HTTP 302 → carlos deleted → lab solved.

---

## Key Insight

```
SSRF filter: "Only allow URLs that are local"
Open redirect: "Redirect to anything in path="

Chain:
  stockApi = /product/nextProduct?path=http://192.168.0.12:8080/admin
              ↑ local path — filter passes
                                    ↑ redirect destination — no validation
```

The filter checks the URL before the request is made.
By the time the redirect fires, the filter has already been satisfied.

---

## Folder Structure

```
ssrf-open-redirect-bypass/
├── exploit/
│   ├── payloads.txt       # All payloads ordered by stage
│   ├── request.txt        # Exact Burp Repeater requests
│   └── response.txt       # Expected responses at each stage
├── fix/
│   ├── fix.java           # Fixed Java (Spring Boot)
│   ├── fix.php            # Fixed PHP
│   └── fix.py             # Fixed Python (Flask)
├── notes/
│   ├── explanation.txt    # Why both vulnerabilities exist
│   └── methodology.txt    # Step-by-step attack methodology
├── vuln/
│   ├── vuln.java          # Vulnerable Java — both bugs
│   ├── vuln.php           # Vulnerable PHP — both bugs
│   └── vuln.py            # Vulnerable Python — both bugs
└── README.md
```

---

## References

- https://portswigger.net/web-security/ssrf/lab-ssrf-filter-bypass-via-open-redirection
- https://portswigger.net/web-security/ssrf#circumventing-common-ssrf-defenses
- https://portswigger.net/web-security/dom-based/open-redirection
- CWE-918: Server-Side Request Forgery
- CWE-601: URL Redirection to Untrusted Site (Open Redirect)
