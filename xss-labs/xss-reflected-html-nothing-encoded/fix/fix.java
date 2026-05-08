// FIX: HTML-encode user input with OWASP Java Encoder before reflecting
import jakarta.servlet.http.*;
import org.owasp.encoder.Encode;
import java.io.*;

public class SearchServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse res)
            throws IOException {
        String query = req.getParameter("search");
        res.setContentType("text/html; charset=UTF-8");
        PrintWriter out = res.getWriter();
        // FIX: Encode.forHtml() converts < > " ' & to HTML entities
        out.println("<html><body><p>Results for: "
                    + Encode.forHtml(query) + "</p></body></html>");
    }
}
