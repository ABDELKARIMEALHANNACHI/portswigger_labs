// FIX: Encode.forHtml() on every stored value at render time
import org.owasp.encoder.Encode;
// ... (same servlet structure, fix in doGet):
// sb.append("<p>").append(Encode.forHtml(rs.getString(1))).append("</p>");
