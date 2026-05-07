// VULNERABLE: GraphQL served at /internal/graphql with no auth
// Introspection fully enabled — schema fully queryable by anyone
package com.lab.graphql;

import org.springframework.graphql.data.method.annotation.*;
import org.springframework.stereotype.Controller;
import java.util.*;

record User(int id, String username, String email, boolean isAdmin) {}

@Controller
public class HiddenEndpointController {

    private static final Map<Integer, User> USERS = new HashMap<>(Map.of(
        1, new User(1, "admin", "admin@corp.com", true)
    ));

    @QueryMapping
    public User getUser(@Argument int id) { return USERS.get(id); }

    @QueryMapping
    public List<User> listUsers() { return new ArrayList<>(USERS.values()); }

    @MutationMapping
    // VULN: no auth — anyone can delete users
    public boolean deleteUser(@Argument int id) { return USERS.remove(id) != null; }

    @MutationMapping
    // VULN: no auth — anyone can change any user's email
    public User changeEmail(@Argument int id, @Argument String email) {
        if (USERS.containsKey(id)) {
            var u = USERS.get(id);
            USERS.put(id, new User(u.id(), u.username(), email, u.isAdmin()));
            return USERS.get(id);
        }
        return null;
    }
}
