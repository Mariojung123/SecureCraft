import com.sun.net.httpserver.HttpServer;
import org.json.JSONObject;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HashMap;
import java.util.Map;

/**
 * SecureCraft – Weak Password Hashing (Java)
 *
 * CHALLENGE: Passwords are hashed with MD5, which is fast and easily cracked.
 * Fix: Use BCrypt (or PBKDF2) instead of MD5.
 *
 * Note: Add the dependency to your build:
 *   Maven: org.mindrot:jbcrypt:0.4
 *   Gradle: implementation 'org.mindrot:jbcrypt:0.4'
 */
public class skeleton_java {

    static final Map<String, String> users = new HashMap<>();

    // ─── VULNERABLE methods – fix these ─────────────────────────────────────────

    /**
     * VULNERABLE: MD5 is cryptographically broken and trivially reversible
     * with rainbow tables / GPU cracking.
     *
     * Fix: replace with BCrypt.hashpw(password, BCrypt.gensalt(12))
     */
    static String hashPassword(String password) throws Exception {
        // VULNERABLE: MD5 is fast — attackers can crack billions per second
        MessageDigest md = MessageDigest.getInstance("MD5");
        byte[] digest = md.digest(password.getBytes(StandardCharsets.UTF_8));
        StringBuilder sb = new StringBuilder();
        for (byte b : digest) sb.append(String.format("%02x", b));
        return sb.toString();
    }

    /**
     * VULNERABLE: comparison still uses MD5.
     * Fix: replace with BCrypt.checkpw(password, stored)
     */
    static boolean verifyPassword(String password, String stored) throws Exception {
        return hashPassword(password).equals(stored);
    }

    // ─── HTTP server boilerplate ─────────────────────────────────────────────────

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);

        server.createContext("/", ex -> {
            String path   = ex.getRequestURI().getPath();
            String method = ex.getRequestMethod();

            if (path.equals("/register") && method.equals("POST")) {
                JSONObject req = new JSONObject(new String(ex.getRequestBody().readAllBytes(), StandardCharsets.UTF_8));
                String username = req.optString("username", "");
                String password = req.optString("password", "");
                try {
                    users.put(username, hashPassword(password));
                    respond(ex, 200, new JSONObject().put("ok", true));
                } catch (Exception e) { respond(ex, 500, new JSONObject().put("error", e.getMessage())); }
                return;
            }

            if (path.equals("/login") && method.equals("POST")) {
                JSONObject req = new JSONObject(new String(ex.getRequestBody().readAllBytes(), StandardCharsets.UTF_8));
                String username = req.optString("username", "");
                String password = req.optString("password", "");
                String stored   = users.get(username);
                try {
                    if (stored != null && verifyPassword(password, stored))
                        respond(ex, 200, new JSONObject().put("success", true));
                    else
                        respond(ex, 401, new JSONObject().put("success", false));
                } catch (Exception e) { respond(ex, 500, new JSONObject().put("error", e.getMessage())); }
                return;
            }

            if (path.equals("/hash") && method.equals("GET")) {
                String rawQuery = ex.getRequestURI().getQuery();
                String user = "";
                if (rawQuery != null)
                    for (String p : rawQuery.split("&"))
                        if (p.startsWith("user=")) user = java.net.URLDecoder.decode(p.substring(5), StandardCharsets.UTF_8);
                respond(ex, 200, new JSONObject().put("hash", users.getOrDefault(user, "")));
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

    static void respond(com.sun.net.httpserver.HttpExchange ex, int status, JSONObject body) throws IOException {
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
        return "<html><body><h2>Weak Password Hashing Lab (Java)</h2></body></html>"
                .getBytes(StandardCharsets.UTF_8);
    }
}
