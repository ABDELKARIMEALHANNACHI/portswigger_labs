// FIX: Spring Boot + Spring Security — role-based access on GraphQL resolvers
package com.lab.graphql;

import org.springframework.graphql.data.method.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import java.util.*;

record BlogPost(int id, String title, String content, String postPassword, boolean isPublic) {
    BlogPost withoutPassword() { return new BlogPost(id, title, content, null, isPublic); }
}

@Controller
public class BlogController {

    private static final Map<Integer, BlogPost> POSTS = Map.of(
        1, new BlogPost(1, "Welcome", "Hello world", null, true),
        2, new BlogPost(2, "Secret Draft", "Top secret", "peter:Th3SecretPass!", false)
    );

    @QueryMapping
    public BlogPost getBlogPost(@Argument int id) {
        var post = POSTS.get(id);
        if (post == null) return null;
        var auth = SecurityContextHolder.getContext().getAuthentication();
        boolean isAdmin = auth != null && auth.getAuthorities().stream()
            .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
        // FIX: non-admin cannot see private posts
        if (!post.isPublic() && !isAdmin) return null;
        // FIX: strip postPassword unless admin
        return isAdmin ? post : post.withoutPassword();
    }

    @QueryMapping
    public List<BlogPost> getAllPosts() {
        var auth = SecurityContextHolder.getContext().getAuthentication();
        boolean isAdmin = auth != null && auth.getAuthorities().stream()
            .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
        return POSTS.values().stream()
            .filter(p -> isAdmin || p.isPublic())
            .map(p -> isAdmin ? p : p.withoutPassword())
            .toList();
    }
}
