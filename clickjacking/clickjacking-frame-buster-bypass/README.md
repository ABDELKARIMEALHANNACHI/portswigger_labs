# Clickjacking — Frame Buster Bypass

## Lab Reference
PortSwigger Web Security Academy — Clickjacking — Lab 2

## Objective
The target app uses a JavaScript frame-busting script (`if (top != self) top.location = self.location`).
Bypass it using the iframe `sandbox` attribute to disable JavaScript execution inside the iframe,
then perform the same clickjacking attack as Lab 1.

## Key Concept
`sandbox="allow-forms"` — allows form submission but blocks JS execution inside the iframe.
This neutalises the JS frame buster while still allowing the click/form action.

## Quick Start
```bash
python3 vuln/vuln.py --url https://<LAB-ID>.web-security-academy.net
python3 fix/fix.py  --url https://<LAB-ID>.web-security-academy.net
```

## CVSS Score
CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N — **6.5 Medium**

## Mitigation
JavaScript frame busters are **unreliable** — CSP frame-ancestors is the only robust fix.
