# CORS Vulnerabilities — PortSwigger Labs

> Cross-Origin Resource Sharing (CORS) misconfigurations allow attackers to bypass the Same-Origin Policy (SOP) and read sensitive data from other origins using the victim's own browser as the attack vehicle.

---

## What is CORS?

CORS is a browser mechanism that extends SOP by letting servers declare which origins are allowed to read their responses. When misconfigured, it becomes a critical vulnerability.

```
Normal SOP:      evil.com  ─── cannot read ──►  bank.com
CORS bypass:     evil.com  ─── can read  ──►    bank.com  (if misconfigured)
```

The key: the browser does the request — attacker just reads the result.

---

## Labs Covered

| # | Lab | Difficulty | Type |
|---|-----|-----------|------|
| 1 | [Basic Origin Reflection](./basic_origin_reflection/README.md) | Apprentice | Server mirrors any origin blindly |
| 2 | [Trusted Insecure Protocols](./trusted_insecure_protocols/README.md) | Practitioner | CORS + XSS chain via HTTP subdomain |

---

## Attack Prerequisites

All CORS attacks require ALL 3 conditions:

```
1. Server reflects/trusts attacker origin
2. Access-Control-Allow-Credentials: true
3. Victim visits attacker page while logged into target
```

---

## Quick Reference — Misconfiguration Types

```
Type 1 — Blind Reflection
  Any origin you send → reflected back automatically
  Fix: whitelist exact trusted origins

Type 2 — Bad Whitelist (Regex/String bugs)
  Suffix check  → register: evilsite.com (ends with allowed domain)
  Prefix check  → register: allowed.com.evil.net
  Bad regex     → missing anchors ^ $ or unescaped dots
  Fix: use strict anchored regex or Set-based whitelist

Type 3 — Null Origin
  Server whitelists "null" → bypass via sandboxed iframe
  Fix: never whitelist null

Type 4 — XSS + CORS Trust Chain
  Subdomain has XSS → runs JS with trusted origin
  Fix: never trust HTTP subdomains, fix all XSS
```

---

## Repository Structure (per lab)

```
lab_name/
├── README.md          — lab explanation, exploit, analysis
├── docs/              — deep dive notes, diagrams
├── fix/
│   ├── fix.js         — fixed server-side code
│   ├── fix.py         — fixed server-side code (Python)
│   └── notes.md       — why the fix works
├── reports/           — pentest report template
├── screenshots/       — proof of concept images
├── tests/
│   ├── test_vuln.py   — verifies vulnerability exists
│   └── test_fix.py    — verifies fix is effective
└── vuln/
    ├── payloads/
    │   └── payloads.txt  — all working exploit payloads
    ├── vuln_config.json  — vulnerable server config
    ├── vuln.js           — vulnerable server code
    └── vuln.py           — vulnerable server code (Python)
```
