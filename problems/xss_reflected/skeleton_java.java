import com.sun.net.httpserver.HttpServer;
import org.json.JSONObject;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

/**
 * SecureCraft – XSS: Reflected (Java)
 *
 * CHALLENGE: The searchPage() method reflects the query parameter raw into HTML.
 * An attacker can inject: ?q=<script>alert('XSS')</script>
 *
 * Fix: HTML-escape the query string before inserting it into the response.
 */
public class skeleton_java {

    // ─── VULNERABLE method – fix this ───────────────────────────────────────────

    /**
     * VULNERABLE: query is inserted raw into the HTML response.
     * Fix this to escape HTML special characters before rendering.
     *
     * Example fix:
     *   String safe = query
     *       .replace("&", "&amp;")
     *       .replace("<", "&lt;")
     *       .replace(">", "&gt;")
     *       .replace("\"", "&quot;")
     *       .replace("'", "&#x27;");
     */
    static String searchPage(String query) {
        // VULNERABLE: raw query inserted into HTML
        return "<html><body><h1>Results for: " + query + "</h1></body></html>";
    }

    // ─── HTTP server boilerplate ─────────────────────────────────────────────────

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);

        server.createContext("/", ex -> {
            if (!ex.getRequestMethod().equals("GET")) { ex.sendResponseHeaders(405, -1); return; }
            String path = ex.getRequestURI().getPath();
            if (path.equals("/search")) {
                String rawQuery = ex.getRequestURI().getQuery();
                String q = "";
                if (rawQuery != null) {
                    for (String p : rawQuery.split("&")) {
                        if (p.startsWith("q="))
                            q = java.net.URLDecoder.decode(p.substring(2), StandardCharsets.UTF_8);
                    }
                }
                byte[] html = searchPage(q).getBytes(StandardCharsets.UTF_8);
                ex.getResponseHeaders().set("Content-Type", "text/html; charset=utf-8");
                ex.sendResponseHeaders(200, html.length);
                ex.getResponseBody().write(html);
            } else {
                byte[] html = loadResource("templates/index.html");
                ex.getResponseHeaders().set("Content-Type", "text/html; charset=utf-8");
                ex.sendResponseHeaders(200, html.length);
                ex.getResponseBody().write(html);
            }
            ex.getResponseBody().close();
        });

        server.start();
        System.out.println("Server running on http://0.0.0.0:8080");
    }

    static byte[] loadResource(String name) throws IOException {
        try (InputStream is = skeleton_java.class.getResourceAsStream(name)) {
            if (is != null) return is.readAllBytes();
        }
        return "<html><body><h2>XSS Reflected Lab (Java)</h2><form action='/search'><input name='q'><button>Search</button></form></body></html>"
                .getBytes(StandardCharsets.UTF_8);
    }
}
