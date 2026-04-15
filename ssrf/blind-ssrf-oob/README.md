# Blind SSRF via Referer Header (OOB Detection)

## Description
This lab demonstrates a Blind SSRF vulnerability where the Referer header is used by server-side analytics to fetch external URLs.

## Impact
- Out-of-band data exfiltration
- Internal network probing
- Cloud metadata access (in real-world scenarios)

## Detection Method
- Burp Collaborator DNS/HTTP interactions

## Exploitation Flow
1. Load product page
2. Modify Referer header
3. Inject Collaborator URL
4. Observe OOB interaction

## Key Lesson
Blind SSRF requires external detection mechanisms since no response is reflected to the user.
