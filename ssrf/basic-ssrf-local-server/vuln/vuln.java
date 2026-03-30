import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

@RestController
public class StockController {

    private RestTemplate restTemplate = new RestTemplate();

    @PostMapping("/stock")
    public String checkStock(@RequestParam String stockApi) {

        // 🚨 VULNERABLE: user controls full URL
        String response = restTemplate.getForObject(stockApi, String.class);

        return response;
    }
}
