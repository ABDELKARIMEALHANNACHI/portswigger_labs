# Lab 5 — JWT Auth Bypass via jku Header Injection (PRACTITIONER)

## Attack
Point `jku` to attacker-controlled JWKS endpoint. Server fetches attacker's
public key and verifies the forged (admin) token with it.

## Also: SSRF
`jku` can point to internal services — dual vulnerability.

## Fix
Pin JWKS URL in server config. Never read it from token.
