// VULNERABLE: JwtParser configured with both RS256 and HS256 allowed
package com.lab.jwt;

import io.jsonwebtoken.*;
import java.security.PublicKey;
import javax.crypto.spec.SecretKeySpec;

public class AlgoConfusionVuln {

    private final PublicKey rsaPublicKey;

    public AlgoConfusionVuln(PublicKey rsaPublicKey) {
        this.rsaPublicKey = rsaPublicKey;
    }

    public Claims verify(String token) {
        String alg = Jwts.parserBuilder().build()
            .parseClaimsJwt(token.substring(0, token.lastIndexOf('.')))
            .getHeader().getAlgorithm();

        if ("RS256".equals(alg)) {
            return Jwts.parserBuilder().setSigningKey(rsaPublicKey)
                       .build().parseClaimsJws(token).getBody();
        } else if ("HS256".equals(alg)) {
            // VULN: HS256 verification using the RSA public key as HMAC secret
            // This is exactly what the attacker crafts!
            byte[] keyBytes = rsaPublicKey.getEncoded();
            SecretKeySpec hmacKey = new SecretKeySpec(keyBytes, "HmacSHA256");
            return Jwts.parserBuilder().setSigningKey(hmacKey)
                       .build().parseClaimsJws(token).getBody();
        }
        throw new JwtException("Unsupported algorithm");
    }
}
