import java.net.*;
import java.io.*;
import java.util.Scanner;

public class vuln {

    static String request(String urlStr, String referer) throws Exception {

        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

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
