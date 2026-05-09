// VULNERABLE: Reads RSA public key from token's own 'jwk' header
package com.lab.jwt;

import com.nimbusds.jose.*;
import com.nimbusds.jose.jwk.RSAKey;
import com.nimbusds.jwt.*;

public class JwkInjectionVulnService {

    public JWTClaimsSet verify(String token) throws Exception {
        SignedJWT jwt = SignedJWT.parse(token);
        JWSHeader header = jwt.getHeader();

        // VULN: extract key from token's own header — attacker-controlled
        JWK jwk = header.getJWK();
        if (jwk == null) throw new Exception("No JWK in header");

        // Uses attacker's supplied public key to verify attacker's forged signature
        RSASSAVerifier verifier = new RSASSAVerifier(((RSAKey)jwk).toRSAPublicKey());
        if (!jwt.verify(verifier)) throw new Exception("Invalid signature");

        return jwt.getJWTClaimsSet();
    }
}
