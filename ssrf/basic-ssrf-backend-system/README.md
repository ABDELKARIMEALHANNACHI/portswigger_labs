# Basic SSRF Against Another Back-End System

## Lab Info
- **Source**: PortSwigger Web Security Academy
- **Level**: APPRENTICE
- **Category**: SSRF

---

## What This Lab Covers

This lab demonstrates SSRF targeting a **separate internal back-end machine** rather than localhost.
The vulnerable feature is a stock check function that makes server-side HTTP requests to an internal system.
The internal network uses the `192.168.0.X` range and an admin interface runs on port `8080`.

---

## Vulnerability

The application takes a user-supplied URL via the `stockApi` parameter and fetches it server-side
with no validation. An attacker can point this parameter at any internal IP:port combination the
server can reach — including admin interfaces that are never exposed to the internet.

---

## Goal

1. Scan `192.168.0.1` – `192.168.0.255` on port `8080` to find the admin interface.
2. Use the admin interface to delete the user `carlos`.

---

## Solution Steps

1. Visit a product page and click **Check stock**.
2. Intercept the request in Burp Suite — send to **Intruder**.
3. Change `stockApi` value to `http://192.168.0.1:8080/admin`.
4. Highlight the last octet (`1`) → click **Add §**.
5. Payload type → **Numbers** | From: `1` | To: `255` | Step: `1`.
6. Run the attack. Sort by **Status** column — find the single `200` response.
7. Send that request to **Repeater**.
8. Change the path to `/admin/delete?username=carlos`.
9. Send → user deleted → lab solved.

---

## Folder Structure

```
basic-ssrf-backend-system/
├── exploit/
│   ├── payloads.txt       # Intruder payload list (1–255)
│   ├── request.txt        # Captured Burp request
│   └── response.txt       # Admin panel response
├── fix/
│   ├── fix.java
│   ├── fix.php
│   └── fix.py
├── notes/
│   ├── explanation.txt    # Why the vulnerability exists
│   └── methodology.txt    # Step-by-step attack methodology
├── vuln/
│   ├── vuln.java
│   ├── vuln.php
│   └── vuln.py
└── README.md
```

---

## Difference: Local Server vs Back-End System SSRF

| | Local Server | Back-End System |
|---|---|---|
| Target | `127.0.0.1` — the app itself | `192.168.0.X` — a different machine |
| What you bypass | Same-app auth | Network firewall / perimeter |
| Why it works | Localhost = trusted by the app | Internal IP = trusted by the network |
| Impact | Admin access on the web app | Databases, caches, internal APIs |

---

## References

- https://portswigger.net/web-security/ssrf
- https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/
