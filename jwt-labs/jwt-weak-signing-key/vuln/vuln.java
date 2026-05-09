// VULNERABLE: HMAC-SHA256 with weak secret "secret1" — crackable by hashcat
package com.lab.jwt;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import java.nio.charset.StandardCharsets;
import javax.crypto.SecretKey;

public class WeakKeyJwtService {

    // VULN: hardcoded weak secret — appears in common wordlists
    private static final String WEAK_SECRET = "secret1";

    private final SecretKey key = Keys.hmacShaKeyFor(
        WEAK_SECRET.getBytes(StandardCharsets.UTF_8)
    );

    public String issue(String subject) {
        return Jwts.builder().setSubject(subject)
                   .signWith(key).compact();
    }

    public Claims verify(String token) {
        return Jwts.parserBuilder()
                   .setSigningKey(key)
                   .build()
                   .parseClaimsJws(token)
                   .getBody();
    }
}
