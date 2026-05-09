# Fix Notes — Algorithm Confusion Without Exposed Key

## Key Insight
Even without an exposed JWKS endpoint, the RSA public key can be
mathematically derived from two JWT signatures. This is not a vulnerability
in the key — it is the mathematical property of RSA signatures.

## The Real Fix
The algorithm confusion vulnerability (accepting HS256 with an RS256 key)
is what enables the attack. Deriving the public key is just a precondition.

Fix = close the algorithm confusion (pin RS256 only).
Once HS256 is rejected, knowing the public key is irrelevant.

## Defence in Depth
1. `algorithms=["RS256"]` — primary fix.
2. Rotate keys periodically — derived key becomes stale.
3. Use short-lived JWTs — limits attack window.
