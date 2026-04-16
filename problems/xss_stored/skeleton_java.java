import com.sun.net.httpserver.HttpServer;

import java.io.*;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/**
 * SecureCraft – XSS: Stored (Java)
 *
 * CHALLENGE: Comments are stored and rendered raw into HTML.
 * An attacker can store: <script>alert('XSS')</script>
 * which executes for every visitor.
 *
 * Fix: HTML-escape each comment before inserting it into the page.
 */
public class skeleton_java {

    static final List<String> comments = new ArrayList<>();

    // ─── VULNERABLE method – fix this ───────────────────────────────────────────

    /**
     * VULNERABLE: comment text is inserted raw into HTML.
     * Fix this to escape HTML special characters in each comment.
     *
     * Example fix:
     *   String safe = c.replace("&","&amp;").replace("<","&lt;")
     *                   .replace(">","&gt;").replace("\"","&quot;");
     */
    static String renderComments(List<String> commentList) {
        StringBuilder sb = new StringBuilder();
        sb.append("<!DOCTYPE html><html><body>");
        sb.append("<h2>Comments</h2>");
        sb.append("<form method='POST' action='/comment'>");
        sb.append("<input name='text' placeholder='Add a comment...'>");
        sb.append("<button type='submit'>Post</button></form><hr>");
        if (commentList.isEmpty()) {
            sb.append("<p>No comments yet.</p>");
        } else {
            for (String c : commentList) {
                // VULNERABLE: raw insertion of user-supplied text
                sb.append("<div class='comment'><p>").append(c).append("</p></div>");
            }
        }
        sb.append("</body></html>");
        return sb.toString();
    }

    // ─── HTTP server boilerplate ─────────────────────────────────────────────────

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);

        server.createContext("/", ex -> {
            String method = ex.getRequestMethod();
            String path   = ex.getRequestURI().getPath();

            if (path.equals("/comment") && method.equals("POST")) {
                // Parse form body
                String body = new String(ex.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
                String text = "";
                for (String kv : body.split("&")) {
                    if (kv.startsWith("text="))
                        text = URLDecoder.decode(kv.substring(5), StandardCharsets.UTF_8);
                }
                comments.add(text);
                ex.getResponseHeaders().set("Location", "/");
                ex.sendResponseHeaders(302, -1);
                ex.getResponseBody().close();
                return;
            }

            // GET / → render comments
            byte[] html = renderComments(comments).getBytes(StandardCharsets.UTF_8);
            ex.getResponseHeaders().set("Content-Type", "text/html; charset=utf-8");
            ex.sendResponseHeaders(200, html.length);
            ex.getResponseBody().write(html);
            ex.getResponseBody().close();
        });

        server.start();
        System.out.println("Server running on http://0.0.0.0:8080");
    }
}
