// FIX: JJWT — requireAlgorithm rejects 'none' and any unexpected algorithm
package com.lab.jwt;

import io.jsonwebtoken.*;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.Key;

public class SecureJwtVerifier {

    private final Key key;

    public SecureJwtVerifier(String secret) {
        this.key = new SecretKeySpec(
            secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"
        );
    }

    public Claims verify(String token) {
        return Jwts.parserBuilder()
            .setSigningKey(key)
            .requireAlgorithm("HS256")  // FIX: 'none' causes UnsupportedJwtException
            .build()
            .parseClaimsJws(token)
            .getBody();
    }
}
