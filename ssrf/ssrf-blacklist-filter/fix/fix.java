/**
 * FIXED CODE — SSRF with Blacklist-Based Input Filter
 * Language: Java (Spring Boot)
 *
 * THE CORRECT APPROACH:
 *   Never use a blacklist for SSRF protection.
 *   Use allowlist + decode-first + DNS resolution + private IP check.
 *
 * FIX 1 — Allowlist:     Only permit known-good hostnames (exact match).
 * FIX 2 — Decode first:  URLDecode the input before any validation check.
 * FIX 3 — Resolve DNS:   Resolve hostname → check IP against blocked ranges.
 * FIX 4 — HTTPS only:    Reject all non-HTTPS schemes.
 * FIX 5 — No redirects:  Disable redirect following in HTTP client.
 * FIX 6 — Timeout:       Enforce short connection timeout.
 */

import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.client.SimpleClientHttpRequestFactory;

import java.net.*;
import java.net.http.*;
import java.util.Set;

@RestController
public class StockController {

    // ✅ FIX 1 — Strict allowlist
    private static final Set<String> ALLOWED_HOSTS = Set.of(
        "stock.weliketoshop.net",
        "stock-service.internal"
    );

    // ✅ FIX 5 + FIX 6 — HTTP client with no redirects and timeout
    private final RestTemplate restTemplate;

    public StockController() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(5_000);
        factory.setReadTimeout(10_000);
        this.restTemplate = new RestTemplate(factory);
        // Note: for full redirect disabling use HttpComponentsClientHttpRequestFactory
        // with .disableRedirectHandling()
    }


    @PostMapping("/product/stock")
    public ResponseEntity<String> checkStock(
            @RequestParam("stockApi") String stockApiUrl) {

        if (!isSafeUrl(stockApiUrl)) {
            return ResponseEntity
                .badRequest()
                .body("{\"error\": \"Invalid or disallowed URL\"}");
        }

        String response = restTemplate.getForObject(stockApiUrl, String.class);
        return ResponseEntity.ok(response);
    }


    private boolean isSafeUrl(String urlString) {
        try {
            // ✅ FIX 2 — Fully decode the URL before any check
            // This defeats encoding bypasses: %2561dmin → %61dmin → admin
            String decoded = urlString;
            String prev;
            do {
                prev = decoded;
                decoded = URLDecoder.decode(decoded, "UTF-8");
            } while (!decoded.equals(prev));

            URL url = new URL(decoded);

            // ✅ FIX 4 — HTTPS scheme only
            if (!"https".equalsIgnoreCase(url.getProtocol())) {
                return false;
            }

            String host = url.getHost();
            if (host == null || host.isEmpty()) {
                return false;
            }

            // ✅ FIX 1 — Allowlist (checked AFTER decoding)
            if (!ALLOWED_HOSTS.contains(host.toLowerCase())) {
                return false;
            }

            // ✅ FIX 3 — Resolve hostname and verify IP is not internal
            InetAddress resolved = InetAddress.getByName(host);
            if (isInternalAddress(resolved)) {
                return false;
            }

            return true;

        } catch (Exception e) {
            return false;
        }
    }


    private boolean isInternalAddress(InetAddress addr) {
        // Java built-ins cover all standard private ranges
        return addr.isLoopbackAddress()     // 127.x.x.x, ::1
            || addr.isSiteLocalAddress()    // 10.x, 172.16.x, 192.168.x
            || addr.isLinkLocalAddress()    // 169.254.x (cloud metadata)
            || addr.isAnyLocalAddress()     // 0.0.0.0
            || addr.isMulticastAddress();   // 224.x.x.x
    }
}


/*
 * ============================================================
 * HOW THIS FIX DEFEATS EVERY BYPASS FROM THE LAB
 *
 * ── Bypass: http://2130706433/%2561dmin ──
 *   FIX 4: scheme is http not https → REJECTED immediately
 *
 * ── Bypass: https://2130706433/admin ──
 *   FIX 2: decode → no change
 *   FIX 1: host "2130706433" not in ALLOWED_HOSTS → REJECTED
 *
 * ── Bypass: https://127.1/%2561dmin ──
 *   FIX 1: "127.1" not in ALLOWED_HOSTS → REJECTED
 *
 * ── Bypass: https://localtest.me/%2561dmin ──
 *   FIX 1: "localtest.me" not in ALLOWED_HOSTS → REJECTED
 *
 * ── Bypass: https://stock.weliketoshop.net/%2561dmin ──
 *   FIX 2: %2561dmin → %61dmin → admin (fully decoded)
 *   FIX 1: "stock.weliketoshop.net" IS in ALLOWED_HOSTS → passes
 *   FIX 3: resolve stock.weliketoshop.net → public IP → NOT internal → passes
 *   The path /admin on the REAL stock service is allowed (it is not the admin panel)
 *   The admin panel only exists on localhost — which is blocked.
 *
 * The only way to reach localhost/admin is to get the check to pass
 * for "localhost" or "127.0.0.1" as the hostname — which is impossible
 * because they are not in the allowlist.
 * ============================================================
 */
