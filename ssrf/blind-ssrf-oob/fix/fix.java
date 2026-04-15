import java.net.*;
import java.io.*;
import java.util.Scanner;
import java.util.List;
import java.util.Arrays;

public class fix {

    // Only allow trusted analytics domain (example strict allowlist)
    private static final List<String> ALLOWED_HOSTS =
        Arrays.asList("vulnerable-lab.net");

    static boolean isAllowed(URL url) {
        String host = url.getHost();

        // strict hostname validation (NO substring matching)
        return ALLOWED_HOSTS.contains(host);
    }

    static String request(String urlStr, String referer) throws Exception {

        URL url = new URL(urlStr);

        // 🔒 BLOCK SSRF BEFORE REQUEST IS MADE
        if (!isAllowed(url)) {
            throw new SecurityException("Blocked: unauthorized host");
        }

        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

        // OPTIONAL HARDENING: sanitize Referer
        if (referer != null && referer.startsWith("http")) {
            URL refUrl = new URL(referer);

            // only allow same origin referer
            if (!ALLOWED_HOSTS.contains(refUrl.getHost())) {
                throw new SecurityException("Blocked: invalid Referer");
            }
        }

        conn.setRequestProperty("Referer", referer);

        BufferedReader in = new BufferedReader(
            new InputStreamReader(conn.getInputStream())
        );

        String inputLine;
        StringBuilder response = new StringBuilder();

        while ((inputLine = in.readLine()) != null) {
            response.append(inputLine);
        }

        in.close();
        return response.toString();
    }

    public static void main(String[] args) throws Exception {

        Scanner scanner = new Scanner(System.in);

        System.out.print("Referer: ");
        String referer = scanner.nextLine();

        String url = "https://vulnerable-lab.net/product";

        System.out.println(request(url, referer));
    }
}
