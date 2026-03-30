import org.springframework.web.bind.annotation.*;
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
