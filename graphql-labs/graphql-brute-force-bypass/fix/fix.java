// FIX: Rate limit enforced inside the resolver using Bucket4j (token bucket algorithm)
// Alias batching now consumes tokens per attempt, not per HTTP request
package com.lab.graphql;

import io.github.bucket4j.*;
import org.springframework.graphql.data.method.annotation.*;
import org.springframework.stereotype.Controller;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

record LoginResult(boolean success, String token, String message) {}

@Controller
public class SecureLoginController {

    private static final Map<String, String> USERS = Map.of(
        "carlos", "abc123",
        "admin", "password123"
    );

    // FIX: per-username token bucket — 5 attempts per minute
    private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();

    private Bucket getBucket(String username) {
        return buckets.computeIfAbsent(username, k ->
            Bucket.builder()
                .addLimit(Bandwidth.classic(5, Refill.greedy(5, Duration.ofMinutes(1))))
                .build()
        );
    }

    @MutationMapping
    public LoginResult login(@Argument String username, @Argument String password) {
        // FIX: consume token INSIDE resolver — each alias consumes one token
        Bucket bucket = getBucket(username);
        if (!bucket.tryConsume(1)) {
            throw new RuntimeException("Too many login attempts. Try again later.");
        }
        if (password.equals(USERS.get(username))) {
            return new LoginResult(true, "jwt-token-for-" + username, "Login successful");
        }
        return new LoginResult(false, null, "Invalid credentials");
    }
}
