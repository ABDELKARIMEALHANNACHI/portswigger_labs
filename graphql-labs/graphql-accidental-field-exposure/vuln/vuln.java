// VULNERABLE: User entity exposes password and role without field-level access control
package com.lab.graphql;

import org.springframework.graphql.data.method.annotation.*;
import org.springframework.stereotype.Controller;
import java.util.*;

// VULN: JPA entity mapped directly to GraphQL type — password hash leaks
record User(int id, String username, String email, String password, String role) {}

@Controller
public class UserController {

    private static final Map<Integer, User> USERS = Map.of(
        1, new User(1, "admin", "admin@corp.com", "supersecret123", "ADMIN"),
        2, new User(2, "carlos", "carlos@corp.com", "hunter2", "USER")
    );

    @QueryMapping
    // VULN: resolves full User including password
    public User getUser(@Argument int id) {
        return USERS.get(id);
    }
}
