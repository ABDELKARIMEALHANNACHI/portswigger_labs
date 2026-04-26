# Clickjacking — Prefilled Form

## Lab Reference
PortSwigger Web Security Academy — Clickjacking — Lab 4

## Objective
The target app has a form that accepts URL parameters to pre-fill input fields.
Use URL parameters to pre-fill the email field in the "Change email" form,
then use clickjacking to make the victim submit the pre-filled form.

## Technique
- Craft a URL with GET parameters that pre-fill form fields:
  `/my-account?email=attacker@evil.com`
- Iframe this URL
- Victim clicks → form is submitted with attacker's email

## Quick Start
```bash
python3 vuln/vuln.py --url https://<LAB-ID>.web-security-academy.net/my-account \
                     --param email --value attacker@evil.com
```

## CVSS Score
CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N — **6.5 Medium**
