// VULNERABLE: Rate limit on HTTP request, not on individual login resolver calls
// Alias batching evades the request-level rate limiter
package com.lab.graphql;

import org.springframework.graphql.data.method.annotation.*;
import org.springframework.stereotype.Controller;
import java.util.*;

record LoginResult(boolean success, String token, String message) {}

@Controller
public class LoginController {

    private static final Map<String, String> USERS = Map.of(
        "carlos", "abc123",
        "admin", "password123"
    );

    @MutationMapping
    // VULN: @RateLimiter annotation is at HTTP level — alias batching bypasses it
    public LoginResult login(@Argument String username, @Argument String password) {
        if (password.equals(USERS.get(username))) {
            return new LoginResult(true, "jwt-token-for-" + username, "Login successful");
        }
        return new LoginResult(false, null, "Invalid credentials");
    }
}
