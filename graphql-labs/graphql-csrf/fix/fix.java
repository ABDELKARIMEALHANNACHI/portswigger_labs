// FIX: CSRF protection via:
// 1. JSON-only content type enforcement (Spring filter)
// 2. SameSite=Strict session cookie
// 3. Custom header requirement (X-Requested-With)
package com.lab.graphql;

import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.*;
import org.springframework.graphql.data.method.annotation.*;
import org.springframework.session.web.http.DefaultCookieSerializer;
import org.springframework.stereotype.Controller;
import java.io.IOException;
import java.util.*;

record User(int id, String username, String email) {}

@Controller
public class SecureMutationController {

    private final Map<Integer, User> users = new HashMap<>(Map.of(
        1, new User(1, "admin", "admin@corp.com")
    ));

    @MutationMapping
    public User changeEmail(@Argument String email) {
        users.put(1, new User(1, "admin", email));
        return users.get(1);
    }
}

@Configuration
class SecurityConfig {

    // FIX: enforce JSON content-type — blocks form-based CSRF
    @Bean
    public FilterRegistrationBean<Filter> contentTypeFilter() {
        FilterRegistrationBean<Filter> bean = new FilterRegistrationBean<>();
        bean.setFilter(new Filter() {
            @Override
            public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
                    throws IOException, ServletException {
                HttpServletRequest httpReq = (HttpServletRequest) req;
                HttpServletResponse httpRes = (HttpServletResponse) res;
                String ct = httpReq.getContentType();
                String xrw = httpReq.getHeader("X-Requested-With");
                if ("POST".equals(httpReq.getMethod()) &&
                    httpReq.getRequestURI().contains("/graphql")) {
                    if (ct == null || !ct.contains("application/json")) {
                        httpRes.sendError(415, "Content-Type must be application/json");
                        return;
                    }
                    if (!"XMLHttpRequest".equals(xrw)) {
                        httpRes.sendError(403, "Missing X-Requested-With header");
                        return;
                    }
                }
                chain.doFilter(req, res);
            }
        });
        bean.addUrlPatterns("/graphql");
        return bean;
    }

    // FIX: SameSite=Strict cookie
    @Bean
    public DefaultCookieSerializer cookieSerializer() {
        DefaultCookieSerializer s = new DefaultCookieSerializer();
        s.setSameSite("Strict");
        s.setUseSecureCookie(true);
        s.setUseHttpOnlyCookie(true);
        return s;
    }
}

// application.properties:
// server.servlet.session.cookie.same-site=strict
// spring.graphql.http.get.enabled=false
