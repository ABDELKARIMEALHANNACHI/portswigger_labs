// FIX: 256-bit random secret from environment variable / secrets manager
package com.lab.jwt;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import javax.crypto.SecretKey;
import java.util.Base64;

public class StrongKeyJwtService {

    // FIX: load from env — minimum 256 bits (32 bytes)
    // Never hardcoded. Generate with: openssl rand -base64 32
    private final SecretKey key;

    public StrongKeyJwtService() {
        String envSecret = System.getenv("JWT_SECRET");
        if (envSecret == null || envSecret.length() < 32) {
            throw new IllegalStateException(
                "JWT_SECRET env var must be at least 32 characters"
            );
        }
        this.key = Keys.hmacShaKeyFor(Base64.getDecoder().decode(envSecret));
    }

    public Claims verify(String token) {
        return Jwts.parserBuilder()
                   .setSigningKey(key)
                   .requireAlgorithm("HS256")
                   .build()
                   .parseClaimsJws(token)
                   .getBody();
    }
}
