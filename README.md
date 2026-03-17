# portswigger_labs

> Completing every PortSwigger Web Security Academy lab manually — no extensions, no automation — then reversing the vulnerable code, writing the secure fix, and building a Semgrep rule to detect the pattern in production.

This is not a notes dump. Every lab follows the same full cycle:

```
PENTEST  →  exploit the vulnerability manually with Burp Suite
REVERSE  →  reconstruct the vulnerable code in Python and Java
ANALYZE  →  identify the exact developer mistake that made it possible
FIX      →  write the production-grade secure implementation
DETECT   →  author a Semgrep rule to catch the pattern in CI/CD
```

The goal is not to collect solved labs. The goal is to understand every vulnerability deeply enough to find it in a real codebase, explain it to a developer, fix it properly, and prevent it from shipping again.

---

## Progress

| Category | Status | Progress |
|---|---|---|
| Server-Side Vulnerabilities | ✅ Completed | 52/52 |
| Path Traversal | ✅ Completed | 14/14 |
| File Upload Vulnerabilities | ✅ Completed | 35/35 |
| Web LLM Attacks | ✅ Completed | 17/17 |
| API Testing | ✅ Completed | 29/29 |
| SQL Injection | 🔄 In Progress | 48/51 |
| Authentication | 🔄 In Progress | 46/55 |
| GraphQL API Vulnerabilities | 🔄 In Progress | 1/29 |
| Access Control / Auth Bypass | 🔄 In Progress | — |
| XSS | 🔄 In Progress | — |
| SSRF | 🔄 In Progress | — |
| XXE | 🔄 In Progress | — |
| Template Injection (SSTI) | 🔄 In Progress | — |
| CSRF | 🔴 Not Started | 0/49 |
| CORS | 🔴 Not Started | 0/21 |
| Clickjacking | 🔴 Not Started | 0/19 |
| WebSockets | 🔴 Not Started | 0/19 |
| NoSQL Injection | 🔴 Not Started | 0/24 |
| Prototype Pollution | 🔴 Not Started | 0/65 |
| Race Conditions | 🔴 Not Started | 0/29 |
| Web Cache Deception | 🔴 Not Started | 0/36 |
| Business Logic | 🔴 Not Started | — |
| DOM-Based Vulnerabilities | 🔴 Not Started | — |
| HTTP Request Smuggling | 🔴 Not Started | — |
| OAuth | 🔴 Not Started | — |
| JWT Attacks | 🔴 Not Started | — |

---

## What's inside each lab

```
category/
└── lab-name/
    ├── README.md              ← full write-up: methodology, payload, root cause, fix, Semgrep rule
    ├── vuln/
    │   ├── vuln.py            ← vulnerable code reconstructed in Python
    │   ├── vuln.java          ← vulnerable code reconstructed in Java
    │   ├── vuln_config.json   ← lab metadata
    │   └── payloads/          ← every payload that worked, documented
    ├── fix/
    │   ├── fix.py             ← secure Python implementation
    │   ├── fix.java           ← secure Java implementation
    │   └── notes.md           ← fix explanation + Semgrep detection rule
    ├── tests/
    │   ├── test_vuln.py       ← confirms the vulnerability is reproducible
    │   └── test_fix.py        ← confirms the fix holds
    ├── screenshots/           ← before and after, Burp captures
    ├── reports/               ← pentest-style write-up where relevant
    └── docs/                  ← mindmaps, flow diagrams
```
