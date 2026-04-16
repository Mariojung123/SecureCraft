import com.sun.net.httpserver.HttpServer;
import org.json.JSONObject;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.sql.*;

/**
 * SecureCraft – SQL Injection: Login Bypass (Java)
 *
 * CHALLENGE: The login() method is vulnerable to SQL injection via string concatenation.
 * An attacker can bypass authentication with: username = "' OR '1'='1' --"
 *
 * Fix: Use PreparedStatement with ? placeholders instead of string concatenation.
 */
public class skeleton_java {

    static final String DB_URL = "jdbc:sqlite:/tmp/sqli_login_java.db";

    static Connection getDb() throws SQLException {
        return DriverManager.getConnection(DB_URL);
    }

    static void initDb() throws SQLException {
        try (Connection conn = getDb(); Statement st = conn.createStatement()) {
            st.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)");
            st.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'supersecret123')");
        }
    }

    // ─── VULNERABLE method – fix this ───────────────────────────────────────────

    /**
     * VULNERABLE: username and password are concatenated directly into the SQL string.
     * Fix this to use PreparedStatement with ? placeholders.
     *
     * Example fix:
     *   PreparedStatement ps = conn.prepareStatement(
     *       "SELECT * FROM users WHERE username = ? AND password = ?");
     *   ps.setString(1, username);
     *   ps.setString(2, password);
     */
    static String login(String username, String password) throws SQLException {
        try (Connection conn = getDb(); Statement st = conn.createStatement()) {
            // VULNERABLE: string concatenation allows SQL injection
            String query = "SELECT * FROM users WHERE username = '" + username
                         + "' AND password = '" + password + "'";
            ResultSet rs = st.executeQuery(query);
            if (rs.next()) {
                return rs.getString("username");
            }
        }
        return null;
    }

    // ─── HTTP server boilerplate ─────────────────────────────────────────────────

    public static void main(String[] args) throws Exception {
        initDb();
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);

        server.createContext("/", ex -> {
            if (!ex.getRequestMethod().equals("GET")) { ex.sendResponseHeaders(405, -1); return; }
            byte[] html = loadResource("templates/index.html");
            ex.getResponseHeaders().set("Content-Type", "text/html; charset=utf-8");
            ex.sendResponseHeaders(200, html.length);
            ex.getResponseBody().write(html);
            ex.getResponseBody().close();
        });

        server.createContext("/login", ex -> {
            if (!ex.getRequestMethod().equals("POST")) { ex.sendResponseHeaders(405, -1); return; }
            String body = new String(ex.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
            JSONObject req = new JSONObject(body);
            String username = req.optString("username", "");
            String password = req.optString("password", "");

            JSONObject resp = new JSONObject();
            int status;
            try {
                String user = login(username, password);
                if (user != null) { resp.put("success", true).put("user", user); status = 200; }
                else              { resp.put("success", false); status = 401; }
            } catch (SQLException e) {
                resp.put("success", false).put("error", e.getMessage()); status = 500;
            }
            byte[] out = resp.toString().getBytes(StandardCharsets.UTF_8);
            ex.getResponseHeaders().set("Content-Type", "application/json");
            ex.sendResponseHeaders(status, out.length);
            ex.getResponseBody().write(out);
            ex.getResponseBody().close();
        });

        server.start();
        System.out.println("Server running on http://0.0.0.0:8080");
    }

    static byte[] loadResource(String name) throws IOException {
        try (InputStream is = skeleton_java.class.getResourceAsStream(name)) {
            if (is != null) return is.readAllBytes();
        }
        return "<html><body><h2>SQL Injection Login Lab (Java)</h2></body></html>"
                .getBytes(StandardCharsets.UTF_8);
    }
}
