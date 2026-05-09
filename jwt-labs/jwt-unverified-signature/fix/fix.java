// FIX: io.jsonwebtoken (JJWT) — signature always verified, algorithm pinned
package com.lab.jwt;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import jakarta.servlet.http.*;
import java.security.PublicKey;

public class SecureJwtServlet extends HttpServlet {

    private final PublicKey publicKey; // loaded from keystore/config

    public SecureJwtServlet(PublicKey publicKey) {
        this.publicKey = publicKey;
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse res)
            throws java.io.IOException {
        String auth = req.getHeader("Authorization");
        if (auth == null || !auth.startsWith("Bearer ")) {
            res.sendError(401); return;
        }
        try {
            // FIX: parse + VERIFY signature. requireAlgorithm pins RS256.
            Claims claims = Jwts.parserBuilder()
                .setSigningKey(publicKey)
                .requireAlgorithm("RS256")   // FIX: reject any other algorithm
                .build()
                .parseClaimsJws(auth.substring(7))
                .getBody();

            if ("administrator".equals(claims.getSubject())) {
                res.getWriter().println("{\"message\":\"Welcome admin\"}");
            } else {
                res.sendError(403);
            }
        } catch (JwtException e) {
            res.sendError(401);
        }
    }
}
