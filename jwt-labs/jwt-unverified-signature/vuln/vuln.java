// VULNERABLE: JWT parsed manually — signature bytes ignored
package com.lab.jwt;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.*;
import java.util.*;
import java.util.Base64;

public class JwtServlet extends HttpServlet {

    private static final ObjectMapper mapper = new ObjectMapper();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse res)
            throws java.io.IOException {
        String auth = req.getHeader("Authorization");
        if (auth == null || !auth.startsWith("Bearer ")) {
            res.sendError(401); return;
        }
        String token = auth.substring(7);
        String[] parts = token.split("\\.");
        if (parts.length != 3) { res.sendError(400); return; }

        // VULN: decode payload but NEVER verify signature
        byte[] payloadBytes = Base64.getUrlDecoder().decode(
            parts[1] + "==".substring(parts[1].length() % 4 == 0 ? 2 : parts[1].length() % 4 == 2 ? 0 : 1)
        );
        Map<?,?> payload = mapper.readValue(payloadBytes, Map.class);

        if ("administrator".equals(payload.get("sub"))) {
            res.getWriter().println("{\"message\":\"Welcome admin\"}");
        } else {
            res.sendError(403);
        }
    }
}
