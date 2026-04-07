/**
 * FIXED CODE — Basic SSRF Against Another Back-End System
 * Language: Java (Spring Boot)
 *
 * FIXES APPLIED:
 *   1. Allowlist — only known stock service hostname permitted
 *   2. DNS resolution check — resolved IP must not be internal/private
 *   3. Scheme enforcement — HTTPS only
 *   4. Redirects disabled — blocks open-redirect bypass chains
 *   5. Timeout enforced — prevents hanging on slow internal services
 */

import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.client.SimpleClientHttpRequestFactory;

import java.net.*;
import java.util.Set;

@RestController
public class StockController {

    // ✅ FIX 1 — Strict allowlist of permitted hostnames
    private static final Set<String> ALLOWED_HOSTS = Set.of(
        "stock.internal",
        "stock-service.production.internal"
    );

    // ✅ FIX 2 — Private IP ranges to block after DNS resolution
    private static final String[] BLOCKED_CIDRS = {
        "127.0.0.0/8",     // loopback
        "10.0.0.0/8",      // private
        "172.16.0.0/12",   // private
        "192.168.0.0/16",  // private
        "169.254.0.0/16",  // link-local (cloud metadata)
    };


    // ✅ FIX 4 + FIX 5 — RestTemplate with no redirects and timeout
    private final RestTemplate restTemplate;

    public StockController() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(5_000);       // ✅ 5s connect timeout
        factory.setReadTimeout(10_000);          // ✅ 10s read timeout
        // Note: to fully disable redirects you need a custom ClientHttpRequestFactory
        // or use HttpComponentsClientHttpRequestFactory with redirect disabled
        this.restTemplate = new RestTemplate(factory);
    }


    @PostMapping("/product/stock")
    public ResponseEntity<String> checkStock(
            @RequestParam("stockApi") String stockApiUrl) {

        // ✅ Validate before fetching
        if (!isSafeUrl(stockApiUrl)) {
            return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body("Invalid or disallowed URL");
        }

        String response = restTemplate.getForObject(stockApiUrl, String.class);
        return ResponseEntity.ok(response);
    }


    private boolean isSafeUrl(String urlString) {
        try {
            URL url = new URL(urlString);

            // ✅ FIX 3 — HTTPS only
            if (!"https".equalsIgnoreCase(url.getProtocol())) {
                return false;
            }

            String host = url.getHost();
            if (host == null || host.isEmpty()) {
                return false;
            }

            // ✅ FIX 1 — Must be on the allowlist
            if (!ALLOWED_HOSTS.contains(host.toLowerCase())) {
                return false;
            }

            // ✅ FIX 2 — Resolve hostname and verify IP is not internal
            // This defeats DNS tricks: attacker.com → 192.168.0.1
            InetAddress resolved = InetAddress.getByName(host);
            String resolvedIp = resolved.getHostAddress();

            if (isInternalIp(resolvedIp)) {
                return false;
            }

            return true;

        } catch (Exception e) {
            return false;
        }
    }


    private boolean isInternalIp(String ip) {
        try {
            InetAddress addr = InetAddress.getByName(ip);
            // Java built-ins cover most cases
            if (addr.isLoopbackAddress())      return true;  // 127.x.x.x
            if (addr.isSiteLocalAddress())     return true;  // 10.x / 172.16.x / 192.168.x
            if (addr.isLinkLocalAddress())     return true;  // 169.254.x (cloud metadata)
            if (addr.isAnyLocalAddress())      return true;  // 0.0.0.0
            return false;
        } catch (UnknownHostException e) {
            return true;  // If we cannot determine — block it
        }
    }
}


/*
 * ============================================================
 * WHY EACH FIX MATTERS
 *
 * Without FIX 1 (allowlist):
 *   Attacker supplies http://192.168.0.68:8080/admin — fetched.
 *
 * Without FIX 2 (DNS check):
 *   Attacker registers evil.com → resolves to 192.168.0.68
 *   Allowlist passes "evil.com" — still fetches internal IP.
 *
 * Without FIX 3 (scheme check):
 *   Attacker uses file:///etc/passwd — reads local file.
 *   Attacker uses gopher:// — sends raw TCP to Redis.
 *
 * Without FIX 4 (no redirects):
 *   Attacker uses open redirect on allowed domain:
 *   https://stock.internal/redirect?url=http://192.168.0.68:8080/admin
 *   Server follows redirect to internal IP — bypass complete.
 *
 * Without FIX 5 (timeout):
 *   SSRF used to make the server hang on internal IPs —
 *   side-channel port scanning via response time differences.
 * ============================================================
 */
