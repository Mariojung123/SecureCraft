import com.sun.net.httpserver.HttpServer;
import org.json.JSONObject;

import java.io.*;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

/**
 * SecureCraft – Path Traversal (Java)
 *
 * CHALLENGE: The getFile() method joins user input to BASE_DIR without
 * verifying the resolved path stays inside BASE_DIR.
 * An attacker can read: ?file=../../etc/passwd
 *
 * Fix: Resolve the canonical path and confirm it starts with BASE_DIR.
 */
public class skeleton_java {

    static final Path BASE_DIR = Path.of("/app/files");

    // ─── VULNERABLE method – fix this ───────────────────────────────────────────

    /**
     * VULNERABLE: filename is joined to BASE_DIR without checking path escape.
     * Fix this to use Path.toRealPath() (or normalize + startsWith) to verify
     * the resolved path is still inside BASE_DIR.
     *
     * Example fix:
     *   Path resolved = BASE_DIR.resolve(filename).normalize();
     *   if (!resolved.startsWith(BASE_DIR)) throw new SecurityException("Access denied");
     */
    static String getFile(String filename) throws IOException {
        // VULNERABLE: no traversal check
        Path path = BASE_DIR.resolve(filename);
        if (!Files.isRegularFile(path)) return null;
        return Files.readString(path);
    }

    // ─── HTTP server boilerplate ─────────────────────────────────────────────────

    public static void main(String[] args) throws Exception {
        // Seed files
        Files.createDirectories(BASE_DIR);
        Files.writeString(BASE_DIR.resolve("public.txt"), "This file is public.");

        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);

        server.createContext("/", ex -> {
            String path = ex.getRequestURI().getPath();

            if (path.equals("/download") && ex.getRequestMethod().equals("GET")) {
                String rawQuery = ex.getRequestURI().getQuery();
                String file = "";
                if (rawQuery != null) {
                    for (String p : rawQuery.split("&")) {
                        if (p.startsWith("file="))
                            file = URLDecoder.decode(p.substring(5), StandardCharsets.UTF_8);
                    }
                }
                JSONObject resp = new JSONObject();
                int status;
                try {
                    String content = getFile(file);
                    if (content == null) { resp.put("error", "Not found"); status = 404; }
                    else                 { resp.put("content", content);    status = 200; }
                } catch (Exception e) {
                    resp.put("error", e.getMessage()); status = 403;
                }
                byte[] out = resp.toString().getBytes(StandardCharsets.UTF_8);
                ex.getResponseHeaders().set("Content-Type", "application/json");
                ex.sendResponseHeaders(status, out.length);
                ex.getResponseBody().write(out);
                ex.getResponseBody().close();
                return;
            }

            byte[] html = loadResource("templates/index.html");
            ex.getResponseHeaders().set("Content-Type", "text/html; charset=utf-8");
            ex.sendResponseHeaders(200, html.length);
            ex.getResponseBody().write(html);
            ex.getResponseBody().close();
        });

        server.start();
        System.out.println("Server running on http://0.0.0.0:8080");
    }

    static byte[] loadResource(String name) throws IOException {
        try (InputStream is = skeleton_java.class.getResourceAsStream(name)) {
            if (is != null) return is.readAllBytes();
        }
        return "<html><body><h2>Path Traversal Lab (Java)</h2></body></html>"
                .getBytes(StandardCharsets.UTF_8);
    }
}
