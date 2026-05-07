// FIX: Spring Security + GraphQL — require auth for mutations
// Introspection disabled via application properties
package com.lab.graphql;

import org.springframework.graphql.data.method.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.stereotype.Controller;
import java.util.*;

record UserPublic(int id, String username, String email) {}

@Controller
@EnableMethodSecurity
public class SecureEndpointController {

    private final Map<Integer, UserPublic> users = new HashMap<>(Map.of(
        1, new UserPublic(1, "admin", "admin@corp.com")
    ));

    @QueryMapping
    public UserPublic getUser(@Argument int id) { return users.get(id); }

    @MutationMapping
    @PreAuthorize("hasRole('ADMIN')")  // FIX: admin only
    public UserPublic changeEmail(@Argument int id, @Argument String email) {
        if (users.containsKey(id)) {
            var u = users.get(id);
            users.put(id, new UserPublic(u.id(), u.username(), email));
            return users.get(id);
        }
        return null;
    }
}

// application.properties:
// spring.graphql.schema.introspection.enabled=false
