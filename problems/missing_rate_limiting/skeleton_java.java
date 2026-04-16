import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import org.json.JSONObject;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * SecureCraft – Missing Rate Limiting (Java)
 *
 * CHALLENGE: The /login endpoint allows unlimited login attempts per IP.
 * An attacker can brute-force passwords with no restriction.
 *
 * Fix: Track attempt counts per IP; return 429 after 5 failed attempts in 60 seconds.
 */
public class skeleton_java {

    static final Map<String, String> USERS = Map.of("admin", "correct_password");

    // ─── VULNERABLE method – fix this ───────────────────────────────────────────

    /**
     * VULNERABLE: always returns false – no rate limiting at all.
     *
     * Fix: Use a ConcurrentHashMap to record (attemptCount, windowStart) per IP.
     * Reset the count when 60 seconds have elapsed; block when count >= 5.
     *
     * Example structure:
     *   record Attempts(int count, long windowStart) {}
     *   static final Map<String, Attempts> attempts = new ConcurrentHashMap<>();
     */
    static boolean isRateLimited(String ip) {
        // TODO: implement rate limiting (max 5 attempts per 60 seconds per IP)
        return false; // VULNERABLE: never rate-limited
    }

    // ─── HTTP server boilerplate ─────────────────────────────────────────────────

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);

        server.createContext("/", ex -> {
            String path   = ex.getRequestURI().getPath();
            String method = ex.getRequestMethod();

            if (path.equals("/login") && method.equals("POST")) {
                String ip = ex.getRemoteAddress().getAddress().getHostAddress();

                if (isRateLimited(ip)) {
                    respond(ex, 429, new JSONObject().put("error", "Too many requests"));
                    return;
                }

                JSONObject req = new JSONObject(new String(ex.getRequestBody().readAllBytes(), StandardCharsets.UTF_8));
                String username = req.optString("username", "");
                String password = req.optString("password", "");

                if (password.equals(USERS.get(username)))
                    respond(ex, 200, new JSONObject().put("success", true));
                else
                    respond(ex, 401, new JSONObject().put("success", false));
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
        return "<html><body><h2>Missing Rate Limiting Lab (Java)</h2></body></html>"
                .getBytes(StandardCharsets.UTF_8);
    }
}
