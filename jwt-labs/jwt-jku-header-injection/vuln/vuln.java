// VULNERABLE: Fetches JWKS from URL in token's 'jku' header — SSRF + key injection
package com.lab.jwt;

import com.nimbusds.jose.*;
import com.nimbusds.jose.jwk.*;
import com.nimbusds.jose.jwk.source.*;
import com.nimbusds.jose.proc.*;
import com.nimbusds.jwt.*;
import com.nimbusds.jwt.proc.*;
import java.net.URL;

public class JkuInjectionVulnService {

    public JWTClaimsSet verify(String token) throws Exception {
        SignedJWT jwt = SignedJWT.parse(token);
        String jkuUrl = (String) jwt.getHeader().getCustomParam("jku");

        // VULN: fetch JWKS from attacker-controlled URL with no validation
        JWKSource<SecurityContext> keySource =
            new RemoteJWKSet<>(new URL(jkuUrl));   // fetches from token's jku

        ConfigurableJWTProcessor<SecurityContext> processor = new DefaultJWTProcessor<>();
        processor.setJWSKeySelector(
            new JWSVerificationKeySelector<>(JWSAlgorithm.RS256, keySource)
        );
        return processor.process(jwt, null);
    }
}
