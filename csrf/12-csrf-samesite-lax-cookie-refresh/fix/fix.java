@Configuration
public class SecurityConfig {

    @Bean
    SecurityFilterChain filterChain(HttpSecurity http)
    throws Exception {

        http
            .csrf(Customizer.withDefaults());

        return http.build();
    }
}
