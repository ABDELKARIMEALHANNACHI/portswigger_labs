// FIX: Single algorithm. Attacker cannot exploit confusion even with derived key.
package com.lab.jwt;

import io.jsonwebtoken.*;
import java.security.PublicKey;

public class FixedAlgoService {
    private final PublicKey rsaPublicKey;

    public FixedAlgoService(PublicKey key) { this.rsaPublicKey = key; }

    public Claims verify(String token) {
        return Jwts.parserBuilder()
            .setSigningKey(rsaPublicKey)
            .requireAlgorithm("RS256")   // FIX: one algorithm, period
            .build()
            .parseClaimsJws(token)
            .getBody();
    }
}
