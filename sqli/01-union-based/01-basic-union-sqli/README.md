
# 01 — Basic UNION-Based SQL Injection

## Objective

Learn how UNION-based SQL Injection works in real-world applications.

This lab focuses on:

* dynamic SQL construction
* UNION SELECT exploitation
* reflected query output
* visible sink discovery
* database fingerprinting basics
* enterprise remediation patterns

## Real-World Context

UNION SQLi is commonly found in:

* search features
* analytics dashboards
* admin panels
* product filtering systems
* legacy reporting platforms

## Attack Goal

Extract unauthorized data by appending arbitrary SELECT statements
to the original backend query.

