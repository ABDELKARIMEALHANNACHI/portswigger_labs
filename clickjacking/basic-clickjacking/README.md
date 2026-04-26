# Basic Clickjacking

## Lab Reference
PortSwigger Web Security Academy — Clickjacking (UI Redressing) — Lab 1

## Objective
Trick the victim into clicking a "Delete account" button on the target application
by overlaying a transparent iframe over a decoy page you control.

## Prerequisites
- A PortSwigger Academy account with the lab active
- The exploit server URL (provided by the lab)
- Basic HTML/CSS knowledge

## Files
| Path | Purpose |
|------|---------|
| `exploit/exploit.html` | Malicious overlay page hosted on exploit server |
| `exploit/payloads.txt` | Quick reference iframe payload snippets |
| `vuln/vuln.py` | Automated detector — confirms site is frameable |
| `fix/fix.py` | Patch verifier — confirms headers block framing |
| `tests/test_vuln.py` | Unit tests for vulnerability detection logic |
| `tests/test_fix.py` | Unit tests for fix verification logic |
| `notes/explanation.txt` | Concept deep-dive |
| `notes/methodology.txt` | Step-by-step attack walkthrough |

## Quick Start
```bash
# 1. Detect vulnerability
python3 vuln/vuln.py --url https://<LAB-ID>.web-security-academy.net

# 2. Serve exploit (use lab's exploit server or python HTTP)
python3 -m http.server 8080

# 3. Verify fix
python3 fix/fix.py --url https://<LAB-ID>.web-security-academy.net
```

## CVSS Score
CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N — **6.5 Medium**

## Mitigation
- Set `X-Frame-Options: DENY` or `SAMEORIGIN`
- Set `Content-Security-Policy: frame-ancestors 'none'`
