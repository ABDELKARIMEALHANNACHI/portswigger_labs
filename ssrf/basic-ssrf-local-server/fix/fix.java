import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Set;

@RestController
public class StockController {

    private RestTemplate restTemplate = new RestTemplate();

    // Allowlist of safe domains
    private static final Set<String> ALLOWED_HOSTS = Set.of("stock.weliketoshop.net");

    @PostMapping("/stock")
    public String checkStock(@RequestParam String stockApi) {

        try {
            URI uri = new URI(stockApi);

            String host = uri.getHost();

            // 🚨 BLOCK non-allowed hosts
            if (host == null || !ALLOWED_HOSTS.contains(host)) {
                return "Blocked: Invalid host";
            }

            // 🚨 BLOCK localhost / IPs
            if (host.equals("localhost") || host.equals("127.0.0.1")) {
                return "Blocked: Internal access denied";
            }

            return restTemplate.getForObject(uri, String.class);

        } catch (URISyntaxException e) {
            return "Invalid URL";
        }
    }
}
