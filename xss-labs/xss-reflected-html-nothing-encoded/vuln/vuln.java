// VULNERABLE: Reflected XSS — PrintWriter writes raw user input into HTML
import jakarta.servlet.http.*;
import java.io.*;

public class SearchServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse res)
            throws IOException {
        String query = req.getParameter("search");
        res.setContentType("text/html");
        PrintWriter out = res.getWriter();
        // VULN: raw concatenation — <script>alert(1)</script> executes
        out.println("<html><body><p>Results for: " + query + "</p></body></html>");
    }
}
