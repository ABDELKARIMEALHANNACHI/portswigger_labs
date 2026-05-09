// VULNERABLE: kid from token header used as file path — path traversal to /dev/null
package com.lab.jwt;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import java.io.*;
import java.nio.file.*;
import javax.crypto.SecretKey;

public class KidPathTraversalVuln {

    private static final String KEYS_DIR = "/opt/keys/";

    public Claims verify(String token) throws Exception {
        String kid = Jwts.parserBuilder()
            .build()
            .parseClaimsJwt(token.substring(0, token.lastIndexOf('.')))
            .getHeader()
            .get("kid", String.class);

        // VULN: kid used as filename — ../../dev/null traverses to /dev/null
        Path keyPath = Paths.get(KEYS_DIR + kid);
        byte[] keyBytes = Files.readAllBytes(keyPath);

        if (keyBytes.length == 0) {
            // /dev/null reads as 0 bytes — empty key
            keyBytes = new byte[0];
        }

        SecretKey key = Keys.hmacShaKeyFor(
            keyBytes.length > 0 ? keyBytes : new byte[32]  // still wrong
        );
        return Jwts.parserBuilder().setSigningKey(key).build()
                   .parseClaimsJws(token).getBody();
    }
}
