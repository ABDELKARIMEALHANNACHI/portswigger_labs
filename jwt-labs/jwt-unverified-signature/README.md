# Lab 1 — JWT Auth Bypass via Unverified Signature (APPRENTICE)

## Attack
Modify payload `sub` claim — signature never verified by server.

## Steps
1. Login → capture JWT
2. Decode payload → change `"sub":"wiener"` to `"sub":"administrator"`
3. Re-encode payload → rebuild token with unchanged signature
4. Access `/admin` endpoint

## Fix
`jwt.decode(token, key, algorithms=["RS256"])` — library verifies signature.
