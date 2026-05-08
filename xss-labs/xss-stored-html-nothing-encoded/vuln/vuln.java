// VULNERABLE: Stored XSS — comment body written to DB raw, rendered without encoding
import jakarta.servlet.http.*;
import java.io.*;
import java.sql.*;
import java.util.*;

public class CommentServlet extends HttpServlet {
    private Connection db;

    @Override
    public void init() throws ServletException {
        try {
            db = DriverManager.getConnection("jdbc:h2:mem:test");
            db.createStatement().execute("CREATE TABLE comments(body VARCHAR(1000))");
        } catch (SQLException e) { throw new ServletException(e); }
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse res)
            throws IOException, ServletException {
        String body = req.getParameter("body");
        try {
            PreparedStatement ps = db.prepareStatement("INSERT INTO comments VALUES(?)");
            ps.setString(1, body);  // stored raw — no sanitization
            ps.executeUpdate();
        } catch (SQLException e) { throw new ServletException(e); }
        res.sendRedirect("/comments");
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse res)
            throws IOException, ServletException {
        res.setContentType("text/html");
        PrintWriter out = res.getWriter();
        try {
            ResultSet rs = db.createStatement().executeQuery("SELECT body FROM comments");
            StringBuilder sb = new StringBuilder("<html><body>");
            while (rs.next()) {
                sb.append("<p>").append(rs.getString(1)).append("</p>"); // VULN: raw
            }
            out.println(sb.append("</body></html>").toString());
        } catch (SQLException e) { throw new ServletException(e); }
    }
}
