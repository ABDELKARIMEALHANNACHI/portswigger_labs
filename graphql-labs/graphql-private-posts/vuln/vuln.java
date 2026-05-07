// VULNERABLE: Spring Boot + GraphQL — no authorization on getBlogPost resolver
package com.lab.graphql;

import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.stereotype.Controller;
import java.util.*;

record BlogPost(int id, String title, String content, String postPassword, boolean isPublic) {}

@Controller
public class BlogController {

    private static final Map<Integer, BlogPost> POSTS = Map.of(
        1, new BlogPost(1, "Welcome", "Hello world", null, true),
        2, new BlogPost(2, "Secret Draft", "Top secret content", "peter:Th3SecretPass!", false)
    );

    @QueryMapping
    // VULN: no @PreAuthorize, no isPublic filter
    public BlogPost getBlogPost(@Argument int id) {
        return POSTS.get(id);
    }

    @QueryMapping
    // VULN: returns all posts including private
    public List<BlogPost> getAllPosts() {
        return new ArrayList<>(POSTS.values());
    }
}
