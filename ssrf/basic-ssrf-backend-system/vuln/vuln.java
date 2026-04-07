/**
 * VULNERABLE CODE — Basic SSRF Against Another Back-End System
 * Language: Java (Spring Boot)
 *
 * WHY THIS IS VULNERABLE:
 *   The stockApi parameter from the POST body is passed directly
 *   to RestTemplate.getForObject() with no validation.
 *   Any URL the attacker supplies will be fetched by the server,
 *   including internal addresses like http://192.168.0.X:8080/admin.
 */

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

@RestController
public class StockController {

    private final RestTemplate restTemplate = new RestTemplate();

    @PostMapping("/product/stock")
    public ResponseEntity<String> checkStock(
            @RequestParam("stockApi") String stockApiUrl) {  // ❌ user controls this

        // No validation — fetches whatever URL the attacker provides
        // Attacker supplies: http://192.168.0.X:8080/admin
        String response = restTemplate.getForObject(stockApiUrl, String.class);

        return ResponseEntity.ok(response);
    }
}


/*
 * ============================================================
 * HOW THE ATTACK WORKS AGAINST THIS CODE
 *
 * Normal:
 *   stockApi=https://stock.internal/product/123
 *   → Fetches stock data, returns it to client
 *
 * Attack — internal host discovery:
 *   stockApi=http://192.168.0.1:8080/admin  (loop 1 through 255)
 *   → RestTemplate fetches the internal admin panel
 *   → One IP returns admin HTML with user management
 *
 * Attack — privilege escalation:
 *   stockApi=http://192.168.0.68:8080/admin/delete?username=carlos
 *   → Server calls internal admin DELETE endpoint
 *   → Admin trusts the request (came from internal network)
 *   → Carlos is deleted
 *
 * Note: Spring's RestTemplate follows redirects by default,
 * which makes open-redirect chains trivially exploitable.
 * ============================================================
 */import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;

@RestController
@RequestMapping("/api")
public class StockController {

    private final RestTemplate restTemplate = new RestTemplate();

    @PostMapping("/stock")
    public ResponseEntity<String> checkStock(@RequestParam String stockApi) {

        try {
            // 🚨 VULNERABLE: user controls internal request target
            ResponseEntity<String> response = restTemplate.exchange(
                    stockApi,
                    HttpMethod.GET,
                    new HttpEntity<>(new HttpHeaders()),
                    String.class
            );

            return ResponseEntity.ok(response.getBody());

        } catch (Exception e) {
            return ResponseEntity.status(500).body("Error fetching stock");
        }
    }
}
