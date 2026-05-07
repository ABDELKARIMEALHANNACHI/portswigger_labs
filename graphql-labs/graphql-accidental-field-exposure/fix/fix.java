// FIX: Separate UserResponse DTO — password/role never exposed.
// Introspection disabled via Spring Boot config.
package com.lab.graphql;

import org.springframework.boot.autoconfigure.graphql.GraphQlProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.graphql.data.method.annotation.*;
import org.springframework.stereotype.Controller;
import java.util.*;

// FIX: Safe DTO — no password, no role
record UserPublicDTO(int id, String username) {}

@Controller
public class UserController {

    private static final Map<Integer, Map<String,Object>> USERS = Map.of(
        1, Map.of("id",1,"username","admin","email","admin@corp.com","_password","hash","_role","ADMIN"),
        2, Map.of("id",2,"username","carlos","email","carlos@corp.com","_password","hash","_role","USER")
    );

    @QueryMapping
    public UserPublicDTO getUser(@Argument int id) {
        var u = USERS.get(id);
        if (u == null) return null;
        // FIX: only return public-safe DTO
        return new UserPublicDTO((int)u.get("id"), (String)u.get("username"));
    }
}

// FIX: Disable introspection in application.properties:
// spring.graphql.schema.introspection.enabled=false
@Configuration
class GraphQLConfig {
    @Bean
    public GraphQlProperties.Schema.Introspection introspection() {
        var i = new GraphQlProperties.Schema.Introspection();
        i.setEnabled(false);  // production setting
        return i;
    }
}
