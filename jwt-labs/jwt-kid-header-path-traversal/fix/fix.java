// FIX: kid resolved via in-memory Map — no filesystem access
package com.lab.jwt;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Map;

public class SecureKidService {

    // FIX: keys in memory — kid is just a Map key, never a file path
    private static final Map<String, SecretKey> KEYS = Map.of(
        "key-2024-01", Keys.hmacShaKeyFor("super-random-256-bit-secret-v1".getBytes(StandardCharsets.UTF_8)),
        "key-2024-02", Keys.hmacShaKeyFor("super-random-256-bit-secret-v2".getBytes(StandardCharsets.UTF_8))
    );

    public Claims verify(String token) {
        String kid = Jwts.parserBuilder().build()
            .parseClaimsJwt(token.substring(0, token.lastIndexOf('.')))
            .getHeader().get("kid", String.class);

        SecretKey key = KEYS.get(kid);
        if (key == null)
            throw new JwtException("Unknown kid: " + kid);

        return Jwts.parserBuilder()
            .setSigningKey(key)
            .requireAlgorithm("HS256")
            .build()
            .parseClaimsJws(token)
            .getBody();
    }
}
