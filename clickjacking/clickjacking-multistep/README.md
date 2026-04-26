# Clickjacking — Multistep

## Lab Reference
PortSwigger Web Security Academy — Clickjacking — Lab 3

## Objective
Some actions require multiple interactions (e.g., click "Delete account" then confirm "Yes").
Design a multistep clickjacking exploit that guides the victim through both clicks.

## Technique
- Two overlapping decoy elements
- Two iframes OR one iframe with CSS transition between steps
- JavaScript controls which decoy step is visible

## Quick Start
```bash
python3 vuln/vuln.py --url https://<LAB-ID>.web-security-academy.net
```

## CVSS Score
CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N — **5.9 Medium**
(AC:H because multiple steps required)
