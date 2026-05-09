// VULNERABLE: Custom JWT verifier that short-circuits on alg=none
package com.lab.jwt;

import java.util.*;
import java.util.Base64;
import com.fasterxml.jackson.databind.ObjectMapper;

public class FlawedJwtVerifier {

    private final String secret;
    private static final ObjectMapper mapper = new ObjectMapper();

    public FlawedJwtVerifier(String secret) { this.secret = secret; }

    @SuppressWarnings("unchecked")
    public Map<String,Object> verify(String token) throws Exception {
        String[] parts = token.split("\\.");
        Map<String,Object> header  = mapper.readValue(decode(parts[0]), Map.class);
        Map<String,Object> payload = mapper.readValue(decode(parts[1]), Map.class);

        String alg = (String) header.getOrDefault("alg", "");

        // VULN: algorithm 'none' explicitly allowed — no signature needed
        if ("none".equalsIgnoreCase(alg)) {
            return payload;
        }
        // ... HMAC verification for HS256 omitted for brevity
        throw new SecurityException("Verification failed");
    }

    private byte[] decode(String s) {
        return Base64.getUrlDecoder().decode(s + "==".substring(s.length() % 4));
    }
}
