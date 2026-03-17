# portswigger_labs

Manual exploitation of every PortSwigger Web Security Academy lab, with the full AppSec cycle applied to each one.

## Cycle

```
PENTEST  →  exploit manually, zero extensions
REVERSE  →  find the vulnerable code behind it
ANALYZE  →  understand the exact developer mistake
FIX      →  write the production-grade secure version
DETECT   →  write a Semgrep rule to catch it in CI/CD
```

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
| GraphQL | 🔄 In Progress | 1/29 |
| Auth Bypass / Access Control | 🔄 In Progress | — |
| XSS | 🔄 In Progress | — |
| SSRF | 🔄 In Progress | — |
| XXE | 🔄 In Progress | — |
| Template Injection SSTI | 🔄 In Progress | — |
| CSRF | 🔴 Not Started | 0/49 |
| CORS | 🔴 Not Started | 0/21 |
| Clickjacking | 🔴 Not Started | 0/19 |
| WebSockets | 🔴 Not Started | 0/19 |
| NoSQL Injection | 🔴 Not Started | 0/24 |
| Prototype Pollution | 🔴 Not Started | 0/65 |
| Race Conditions | 🔴 Not Started | 0/29 |
| Web Cache Deception | 🔴 Not Started | 0/36 |
| Business Logic | 🔴 Not Started | — |
| DOM-Based | 🔴 Not Started | — |
| HTTP Request Smuggling | 🔴 Not Started | — |
| OAuth | 🔴 Not Started | — |
| JWT Attacks | 🔴 Not Started | — |

## Lab Structure

```
category/
└── lab-name/
    ├── README.md
    ├── vuln/
    │   ├── vuln.py
    │   ├── vuln.java
    │   ├── vuln_config.json
    │   └── payloads/
    ├── fix/
    │   ├── fix.py
    │   ├── fix.java
    │   └── notes.md
    ├── tests/
    │   ├── test_vuln.py
    │   └── test_fix.py
    ├── screenshots/
    ├── reports/
    └── docs/
```
