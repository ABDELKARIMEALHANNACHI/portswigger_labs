# Race Conditions

## Lab Info

| Field | Detail |
|---|---|
| Platform | PortSwigger Web Security Academy |
| Difficulty | Practitioner |
| Status | 🔴 Not started |
| Lab URL | |

---

## Methodology

```
1. RECON    — understand the application behavior
2. IDENTIFY — locate the vulnerable parameter or endpoint
3. EXPLOIT  — craft and deliver the payload manually
4. REVERSE  — find the vulnerable code behind it
5. FIX      — write the production-grade secure version
6. DETECT   — write a Semgrep rule for CI/CD detection
```

---

## Exploit

### Vulnerable Behavior
```
<!-- describe what the app does wrong -->
```

### Payload
```
<!-- paste working payload here -->
```

### Steps
1.
2.
3.

---

## Vulnerable Code

```python
# vuln/vuln.py
```

```java
// vuln/vuln.java
```

---

## Secure Fix

```python
# fix/fix.py
```

```java
// fix/fix.java
```

---

## Semgrep Rule

```yaml
rules:
  - id: detect-lab-01
    message: "Potential Race Conditions"
    severity: ERROR
    languages: [python, java]
    patterns:
      - pattern: |
          # detection pattern here
```

---

## Screenshots

| Exploit | Fix |
|---|---|
| ![exploit](screenshots/exploit.png) | ![fix](screenshots/fix.png) |

---

## Lessons Learned
-
-
-
