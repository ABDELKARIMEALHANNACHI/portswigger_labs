# Lab 4 — JWT Auth Bypass via JWK Header Injection (PRACTITIONER)

## Attack
Embed attacker's RSA public key in `jwk` header. Sign with matching private key.
Server uses embedded key for verification → accepts forged token.

## Fix
Use only server-side trusted keys. Never read verification key from token header.
