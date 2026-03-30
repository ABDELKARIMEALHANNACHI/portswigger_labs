import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;
import java.net.*;
import java.util.Set;

@RestController
@RequestMapping("/api")
public class StockController {

    private final RestTemplate restTemplate = new RestTemplate();

    private static final Set<String> ALLOWED_HOSTS = Set.of("stock.weliketoshop.net");

    private boolean isSafe(URI uri) {
        String host = uri.getHost();

        if (host == null) return false;

        // Allowlist
        if (!ALLOWED_HOSTS.contains(host)) return false;

        // Resolve IP and block private ranges
        try {
            InetAddress address = InetAddress.getByName(host);
            if (address.isAnyLocalAddress() ||
                address.isLoopbackAddress() ||
                address.isSiteLocalAddress()) {
                return false;
            }
        } catch (Exception e) {
            return false;
        }

        return true;
    }

    @PostMapping("/stock")
    public ResponseEntity<String> checkStock(@RequestParam String stockApi) {

        try {
            URI uri = new URI(stockApi);

            if (!isSafe(uri)) {
                return ResponseEntity.status(403).body("Blocked");
            }

            ResponseEntity<String> response =
                restTemplate.getForEntity(uri, String.class);

            return ResponseEntity.ok(response.getBody());

        } catch (Exception e) {
            return ResponseEntity.status(400).body("Invalid request");
        }
    }
}
