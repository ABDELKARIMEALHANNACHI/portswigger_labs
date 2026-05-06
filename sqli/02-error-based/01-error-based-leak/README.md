# 05 — Error-Based SQL Injection

## Objective
Extract data through database error messages.

## Core idea
Force SQL errors that reveal internal data.

## Why this matters
- UNION blocked → fallback technique
- Blind too slow → error-based faster
- Misconfigured production apps leak stack traces
