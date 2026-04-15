/**
 * FIXED CODE — SSRF with Filter Bypass via Open Redirection
 * Language: Java (Spring Boot)
 *
 * TWO BUGS FIXED:
 *
 * FIX 1 — SSRF in StockController:
 *   a) Allowlist specific hostnames
 *   b) URL decoded before validation
 *   c) DNS resolve + private IP check
 *   d) Redirect following DISABLED  ← CRITICAL FIX
 *   e) Timeout enforced
 *
 * FIX 2 — Open Redirect in ProductController:
 *   Validate path is a permitted relative path only.
 *   Reject any absolute URL (http://, https://, //).
 */

import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.client.SimpleClientHttpRequestFactory;

import java.net.*;
import java.util.Set;
import java.util.regex.Pattern;


// ── FIX 1: SSRF Stock Checker ─────────────────────────────────────────────────

@RestController
public class StockController {

    private static final Set<String> ALLOWED_HOSTS = Set.of(
        "stock.weliketoshop.net",
        "stock.internal"
    );

    // ✅ CRITICAL FIX: Custom RestTemplate that does NOT follow redirects
    private final RestTemplate restTemplate;

    public StockController() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory() {
            @Override
            protected void prepareConnection(HttpURLConnection connection, String httpMethod)
                    throws IOException {
                super.prepareConnection(connection, httpMethod);
                // ✅ Disable redirect following at connection level
                connection.setInstanceFollowRedirects(false);
            }
        };
        factory.setConnectTimeout(5_000);
        factory.setReadTimeout(10_000);
        this.restTemplate = new RestTemplate(factory);
    }


    private boolean isSafeUrl(String urlString) {
        try {
            // Decode twice — defeats %2561-style double encoding
            String decodedOnce  = URLDecoder.decode(urlString, "UTF-8");
            String decodedTwice = URLDecoder.decode(decodedOnce, "UTF-8");

            URL url = new URL(decodedTwice);

            // HTTPS only
            if (!"https".equalsIgnoreCase(url.getProtocol())) return false;

            String host = url.getHost();
            if (host == null || host.isEmpty()) return false;

            // Allowlist
            if (!ALLOWED_HOSTS.contains(host.toLowerCase())) return false;

            // DNS resolve + private IP check
            InetAddress resolved = InetAddress.getByName(host);
            if (resolved.isLoopbackAddress())  return false;
            if (resolved.isSiteLocalAddress()) return false;
            if (resolved.isLinkLocalAddress()) return false;
            if (resolved.isAnyLocalAddress())  return false;

            return true;

        } catch (Exception e) {
            return false;
        }
    }


    @PostMapping("/product/stock")
    public ResponseEntity<String> checkStock(
            @RequestParam("stockApi") String stockApiUrl) {

        if (stockApiUrl == null || stockApiUrl.isEmpty()) {
            return ResponseEntity.badRequest().body("stockApi required");
        }

        if (!isSafeUrl(stockApiUrl)) {
            return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body("URL not permitted");
        }

        // ✅ RestTemplate configured with no redirect following
        // Even if the URL returns a 302, it will NOT be followed
        ResponseEntity<String> response = restTemplate.getForEntity(stockApiUrl, String.class);

        // ✅ Reject redirect responses
        if (response.getStatusCode().is3xxRedirection()) {
            return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body("Redirects not permitted");
        }

        return ResponseEntity.ok(response.getBody());
    }
}


// ── FIX 2: Open Redirect ProductController ────────────────────────────────────

@RestController
public class ProductController {

    // ✅ Only allow relative paths to product pages
    private static final Pattern ALLOWED_PATH =
        Pattern.compile("^/product\\?productId=\\d+$");


    @GetMapping("/product/nextProduct")
    public ResponseEntity<Void> nextProduct(@RequestParam String path) {

        // ✅ FIX: validate path before using it in Location header
        // Rejects: http://, https://, //, or anything not matching the pattern
        if (!ALLOWED_PATH.matcher(path).matches()) {
            return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .build();
        }

        return ResponseEntity
            .status(HttpStatus.FOUND)
            .location(URI.create(path))
            .build();
    }
}


/*
 * ============================================================
 * THE MINIMAL ONE-LINE FIX THAT STOPS THIS ATTACK:
 *
 * Before (vulnerable):
 *   private final RestTemplate restTemplate = new RestTemplate();
 *   // Default RestTemplate follows redirects
 *
 * After (fixed):
 *   // Configure factory with redirect disabled
 *   connection.setInstanceFollowRedirects(false);
 *
 * With this fix:
 *   stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin
 *   → RestTemplate fetches local path
 *   → receives 302 Location: http://192.168.0.12:8080/admin
 *   → does NOT follow the redirect
 *   → returns 302 to application
 *   → application rejects 3xx
 *   → chain broken, lab unsolvable
 *
 * Always disable redirect following in server-side HTTP clients
 * that fetch user-supplied URLs. This is the rule.
 * ============================================================
 */
