/**
 * VULNERABLE CODE — SSRF with Blacklist-Based Input Filter
 * Language: Java (Spring Boot)
 *
 * WHAT THIS SIMULATES:
 *   A developer patched their SSRF endpoint with a string-based blacklist.
 *   The blacklist checks raw undecoded input.
 *   RestTemplate decodes URLs before making connections.
 *   The gap between check and execution is the bypass.
 *
 * TWO DEFENSES DEPLOYED (both broken):
 *   1. Block "127.0.0.1" and "localhost" (case-insensitive substring match)
 *   2. Block "/admin" in the URL path (case-insensitive substring match)
 */

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@RestController
public class StockController {

    private final RestTemplate restTemplate = new RestTemplate();

    // ❌ DEFENSE 1 — Raw substring match, no resolution, no decoding
    private static final List<String> BLOCKED_HOSTS = List.of(
        "127.0.0.1",
        "localhost"
    );

    // ❌ DEFENSE 2 — Raw path substring match, no URL decoding before check
    private static final List<String> BLOCKED_PATHS = List.of(
        "/admin"
    );


    private boolean isBlocked(String url) {
        String urlLower = url.toLowerCase();

        // ❌ String matching only — misses all alternative representations
        // Bypassed by: 2130706433, 127.1, 0x7f000001, [::1], localtest.me
        for (String blocked : BLOCKED_HOSTS) {
            if (urlLower.contains(blocked)) {
                return true;
            }
        }

        // ❌ Path matching on raw input — misses double-encoded paths
        // Bypassed by: /%2561dmin (double-encoded 'a')
        for (String blocked : BLOCKED_PATHS) {
            if (urlLower.contains(blocked)) {
                return true;
            }
        }

        return false;
    }


    @PostMapping("/product/stock")
    public ResponseEntity<String> checkStock(
            @RequestParam("stockApi") String stockApiUrl) {

        // ❌ isBlocked() checks raw input before any decoding
        if (isBlocked(stockApiUrl)) {
            return ResponseEntity
                .badRequest()
                .body("{\"error\": \"External stock check service is not available\"}");
        }

        // RestTemplate decodes the URL before making the connection:
        //   /%2561dmin → /%61dmin → /admin
        //   2130706433 → resolved to 127.0.0.1
        // The filter checked one thing. RestTemplate uses another.
        String response = restTemplate.getForObject(stockApiUrl, String.class);
        return ResponseEntity.ok(response);
    }
}


/*
 * ============================================================
 * HOW THE BYPASS WORKS AGAINST THIS CODE
 *
 * Input:  stockApi=http://2130706433/%2561dmin/delete?username=carlos
 *
 * isBlocked() check:
 *   url.toLowerCase() = "http://2130706433/%2561dmin/delete?username=carlos"
 *   contains("127.0.0.1")? No.
 *   contains("localhost")? No.
 *   contains("/admin")? No — because path is /%2561dmin not /admin.
 *   → returns false → PASSES filter
 *
 * RestTemplate execution:
 *   Resolves 2130706433 → 127.0.0.1
 *   Decodes /%2561dmin:
 *     %25 → %
 *     remaining: /%61dmin
 *     %61 → a
 *     final: /admin
 *   Connects to: http://127.0.0.1/admin/delete?username=carlos
 *   Admin deletes carlos. Returns 302.
 *
 * ROOT CAUSE:
 *   isBlocked() and RestTemplate disagree on what the URL means.
 *   isBlocked() sees encoded characters as literal strings.
 *   RestTemplate decodes them before use.
 *   Any defense that checks before decoding can be defeated by encoding.
 * ============================================================
 */
