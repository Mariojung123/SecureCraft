import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import org.json.JSONObject;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.Map;

/**
 * SecureCraft – IDOR: User Data (Java)
 *
 * CHALLENGE: Any authenticated user can access any other user's profile
 * by simply changing the user_id in the URL.
 *
 * Fix: Check that the requesting user's ID matches the target user_id.
 */
public class skeleton_java {

    record UserProfile(int id, String username, String email, String ssn) {
        JSONObject toJson() {
            return new JSONObject()
                    .put("id", id)
                    .put("username", username)
                    .put("email", email)
                    .put("ssn", ssn);
        }
    }

    static final Map<Integer, UserProfile> USERS = Map.of(
            1, new UserProfile(1, "alice", "alice@example.com", "123-45-6789"),
            2, new UserProfile(2, "bob",   "bob@example.com",   "987-65-4321")
    );

    // ─── VULNERABLE method – fix this ───────────────────────────────────────────

    /**
     * VULNERABLE: any authenticated user can retrieve any profile – no ownership check.
     *
     * Fix: verify requestingUserId == targetUserId before returning the profile.
     *
     * Example fix:
     *   if (requestingUserId != targetUserId) throw new SecurityException("Forbidden");
     */
    static JSONObject getProfile(int requestingUserId, int targetUserId) {
        // VULNERABLE: ownership not verified
        UserProfile profile = USERS.get(targetUserId);
        if (profile == null) return null;
        return profile.toJson();
    }

    // ─── HTTP server boilerplate ─────────────────────────────────────────────────

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);

        server.createContext("/", ex -> {
            String path   = ex.getRequestURI().getPath();
            String method = ex.getRequestMethod();

            // GET /profile/{id}
            if (path.startsWith("/profile/") && method.equals("GET")) {
                String idStr = path.substring("/profile/".length());
                int targetId;
                try { targetId = Integer.parseInt(idStr); }
                catch (NumberFormatException e) {
                    respond(ex, 400, new JSONObject().put("error", "Invalid id"));
                    return;
                }

                // Simulate: requester is always user 1 (logged-in user)
                String xUserId = ex.getRequestHeaders().getFirst("X-User-Id");
                int requesterId = xUserId != null ? Integer.parseInt(xUserId) : 1;

                JSONObject profile = getProfile(requesterId, targetId);
                if (profile == null) respond(ex, 404, new JSONObject().put("error", "Not found"));
                else                 respond(ex, 200, profile);
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
        return "<html><body><h2>IDOR Lab (Java)</h2></body></html>"
                .getBytes(StandardCharsets.UTF_8);
    }
}
