// FIX: Server uses its own pre-loaded public key — 'jwk' header param ignored
package com.lab.jwt;

import io.jsonwebtoken.*;
import java.security.PublicKey;

public class SecureJwkService {

    private final PublicKey trustedKey; // loaded from keystore at startup

    public SecureJwkService(PublicKey trustedKey) {
        this.trustedKey = trustedKey;
    }

    public Claims verify(String token) {
        // FIX: JJWT ignores 'jwk'/'jku' header params by design
        // It uses only the key we provide here
        return Jwts.parserBuilder()
            .setSigningKey(trustedKey)
            .requireAlgorithm("RS256")
            .build()
            .parseClaimsJws(token)
            .getBody();
    }
}
