// VULNERABLE: Servlet serves a page; DOM XSS lives in the inline JavaScript.
// The server itself doesn't need to reflect anything — the client does the damage.
import jakarta.servlet.http.*;
import java.io.*;

public class DomWriteServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse res) throws IOException {
        res.setContentType("text/html");
        PrintWriter out = res.getWriter();
        out.println("""
            <!DOCTYPE html><html><body>
            <script>
              // VULN: location.search → document.write — no sanitization
              var qs = location.search.substring(1);
              var params = new URLSearchParams(qs);
              document.write('<img src="/img?q=' + params.get('search') + '">');
            </script>
            </body></html>
        """);
    }
}
