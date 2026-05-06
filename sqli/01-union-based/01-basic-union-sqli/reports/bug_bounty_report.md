
# UNION-Based SQL Injection

## Severity

Critical

## Endpoint

GET /products?category=

## Description

The application is vulnerable to UNION-based SQL Injection due to
unsafe string concatenation inside backend SQL queries.

## Impact

An attacker can:

* extract credentials
* dump database contents
* access sensitive records
* potentially achieve RCE

## Proof of Concept

Payload:

```
' UNION SELECT NULL,username,password FROM users--
```

## Remediation

Use parameterized queries everywhere.

