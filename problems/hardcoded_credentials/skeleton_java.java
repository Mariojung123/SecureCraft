import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import org.json.JSONObject;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.Map;

/**
 * SecureCraft – Hardcoded Credentials (Java)
 *
 * CHALLENGE: The admin API key is hardcoded directly in the source code.
 * Anyone who reads the source (or decompiles the JAR) obtains the secret.
 *
 * Fix: Read the key from an environment variable (System.getenv) instead.
 */
public class skeleton_java {

    // ─── VULNERABLE constant – fix this ─────────────────────────────────────────

    /**
     * VULNERABLE: secret is hardcoded — visible in source, git history, and decompiled bytecode.
     *
     * Fix: replace with System.getenv("ADMIN_API_KEY")
     * and ensure the app fails fast (or logs a warning) when the variable is missing.
     */
    static final String ADMIN_API_KEY = "super_secret_admin_key_1234"; // VULNERABLE

    static boolean checkApiKey(String provided) {
        return provided.equals(ADMIN_API_KEY);
    }

    // ─── HTTP server boilerplate ─────────────────────────────────────────────────

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);

        server.createContext("/", ex -> {
            String path   = ex.getRequestURI().getPath();
            String method = ex.getRequestMethod();

            if (path.equals("/admin") && method.equals("GET")) {
                String key = ex.getRequestHeaders().getFirst("X-Api-Key");
                if (key == null) key = "";

                if (!checkApiKey(key))
                    respond(ex, 401, new JSONObject().put("error", "Unauthorized"));
                else
                    respond(ex, 200, new JSONObject().put("data", "Sensitive admin data"));
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

    static void respond(HttpExchange ex, int status, JSONObject body) throws IOException {
        byte[] out = body.toString().getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", "application/json");
        ex.sendResponseHeaders(status, out.length);
        ex.getResponseBody().write(out);
        ex.getResponseBody().close();
    }

    static byte[] loadResource(String name) throws IOException {
        try (InputStream is = skeleton_java.class.getResourceAsStream(name)) {
            if (is != null) return is.readAllBytes();
        }
        return "<html><body><h2>Hardcoded Credentials Lab (Java)</h2></body></html>"
                .getBytes(StandardCharsets.UTF_8);
    }
}
