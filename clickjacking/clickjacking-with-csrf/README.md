# Clickjacking Combined with CSRF

## Lab Reference
PortSwigger Web Security Academy — Clickjacking — Lab 5

## Objective
Demonstrate how clickjacking bypasses CSRF token protections on a form action.
Even if the application has CSRF tokens, they are useless if the page is frameable,
because the victim's browser sends the request WITH the CSRF token automatically
(loaded from the iframe's authenticated session).

## Key Insight
CSRF tokens prevent forged cross-origin requests.
Clickjacking does NOT forge requests — it USES the victim's own browser to make them.
Therefore CSRF tokens provide NO protection against clickjacking.

## Quick Start
```bash
python3 vuln/vuln.py --url https://<LAB-ID>.web-security-academy.net
```

## CVSS Score
CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N — **6.5 Medium**

## Mitigation
CSRF tokens + Clickjacking protection (CSP frame-ancestors) are BOTH required.
