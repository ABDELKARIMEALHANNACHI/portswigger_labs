// VULNERABLE: GraphQL mutation accepts GET + form-encoded body
// No CSRF token validation. SameSite cookie not enforced.
package com.lab.graphql;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.graphql.data.method.annotation.*;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import java.util.*;

record User(int id, String username, String email) {}

@Controller
public class CsrfVulnController {

    private final Map<Integer, User> users = new HashMap<>(Map.of(
        1, new User(1, "admin", "admin@corp.com")
    ));

    @MutationMapping
    // VULN: no CSRF token check
    public User changeEmail(@Argument String email) {
        users.put(1, new User(1, "admin", email));
        return users.get(1);
    }

    @MutationMapping
    public boolean deleteAccount() {
        users.clear();
        return true;
    }
}

// application.properties (VULNERABLE settings):
// server.servlet.session.cookie.same-site=none   ← allows cross-origin
// spring.graphql.http.GET enabled                ← GET mutations
