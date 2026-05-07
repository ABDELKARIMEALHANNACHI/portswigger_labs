# portswigger_labs

> Completing every PortSwigger Web Security Academy lab manually — no extensions, no automation — then reversing the vulnerable code, writing the secure fix, and authoring a Semgrep rule to catch the pattern in CI/CD.

This is not a notes dump.

Every lab follows the same full cycle:

```
PENTEST  →  exploit the vulnerability manually with Burp Suite
REVERSE  →  reconstruct the vulnerable code in Python and Java
ANALYZE  →  identify the exact developer mistake that made it possible
FIX      →  write the production-grade secure implementation
DETECT   →  author a Semgrep rule to catch the pattern in CI/CD
```

The goal is not to collect solved labs. The goal is to understand every vulnerability deeply enough to **find it in a real codebase**, **explain it to a developer**, **fix it properly**, and **prevent it from shipping again**.

---

## Progress

| Category | Status | Labs |
|---|---|---|
| Server-Side Vulnerabilities | ✅ Completed | 52 / 52 |
| Path Traversal | ✅ Completed | 14 / 14 |
| File Upload Vulnerabilities | ✅ Completed | 35 / 35 |
| SQL Injection | ✅ Completed | 51 / 51 |
| Authentication | ✅ Completed | 55 / 55 |
| Business Logic | ✅ Completed | — |
| Access Control / Auth Bypass | ✅ Completed | — |
| XSS | ✅ Completed | — |
| SSRF | ✅ Completed | — |
| XXE | ✅ Completed | — |
| Template Injection (SSTI) | ✅ Completed | — |
| CSRF | ✅ Completed | 49 / 49 |
| CORS | ✅ Completed | 21 / 21 |
| Clickjacking | ✅ Completed | 19 / 19 |
| WebSockets | ✅ Completed | 19 / 19 |
| NoSQL Injection | ✅ Completed | 24 / 24 |
| Prototype Pollution | ✅ Completed | 65 / 65 |
| Race Conditions | ✅ Completed | 29 / 29 |
| Web Cache Deception | ✅ Completed | 36 / 36 |
| DOM-Based Vulnerabilities | ✅ Completed | — |
| OAuth | ✅ Completed | — |
| JWT Attacks | ✅ Completed | — |
| Web LLM Attacks | ✅ Completed | 17 / 17 |
| API Testing | ✅ Completed | 29 / 29 |
| GraphQL API Vulnerabilities | ✅ Completed | 29 / 29 |
| **HTTP Request Smuggling** | 🔄 **In Progress** | — |

---

## What's inside each lab

Every category follows the same directory contract:

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

---

## Philosophy

Most people who "complete" PortSwigger labs click through the solution and move on. That's not what this is.

Every lab here is treated as a real engagement:
- The vulnerable pattern is reconstructed from scratch — not copied from the lab.
- The fix addresses the **root cause**, not just the symptom.
- The Semgrep rule means the pattern can never silently ship in production again.
- The tests prove both that the vulnerability is real and that the fix is correct.

If you can't write the vulnerable code yourself, you don't fully understand the vulnerability. If you can't write a rule to detect it automatically, you'll miss it in code review.

---

## Semgrep Rules

Every `fix/notes.md` contains a production-ready Semgrep rule for the vulnerability class. Rules cover Python, Java, PHP, and JavaScript where applicable. The full rule collection can be extracted with:

```bash
grep -r "semgrep" --include="notes.md" -A 30 . > semgrep-rules-all.yml
```

---

## References

- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [OWASP Testing Guide v4.2](https://owasp.org/www-project-web-security-testing-guide/)
- [Semgrep Registry](https://semgrep.dev/explore)
