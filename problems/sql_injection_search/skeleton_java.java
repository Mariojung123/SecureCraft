import com.sun.net.httpserver.HttpServer;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.sql.*;

/**
 * SecureCraft – SQL Injection: Search (Java)
 *
 * CHALLENGE: The searchProducts() method is vulnerable to SQL injection.
 * An attacker can dump all data with: keyword = "' OR '1'='1
 *
 * Fix: Use PreparedStatement with ? placeholders instead of string concatenation.
 */
public class skeleton_java {

    static final String DB_URL = "jdbc:sqlite:/tmp/sqli_search_java.db";

    static Connection getDb() throws SQLException {
        return DriverManager.getConnection(DB_URL);
    }

    static void initDb() throws SQLException {
        try (Connection conn = getDb(); Statement st = conn.createStatement()) {
            st.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL)");
            st.execute("INSERT OR IGNORE INTO products VALUES (1,'Laptop',999.99)");
            st.execute("INSERT OR IGNORE INTO products VALUES (2,'Mouse',29.99)");
            st.execute("INSERT OR IGNORE INTO products VALUES (3,'Keyboard',79.99)");
            // Secret table – should NOT be reachable via search
            st.execute("CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY, secret TEXT)");
            st.execute("INSERT OR IGNORE INTO secrets VALUES (1,'FLAG{sql_injection_found}')");
        }
    }

    // ─── VULNERABLE method – fix this ───────────────────────────────────────────

    /**
     * VULNERABLE: keyword is concatenated directly into the LIKE clause.
     * Fix this to use PreparedStatement with a ? placeholder.
     *
     * Example fix:
     *   PreparedStatement ps = conn.prepareStatement(
     *       "SELECT * FROM products WHERE name LIKE ?");
     *   ps.setString(1, "%" + keyword + "%");
     */
    static JSONArray searchProducts(String keyword) throws SQLException {
        JSONArray results = new JSONArray();
        try (Connection conn = getDb(); Statement st = conn.createStatement()) {
            // VULNERABLE: string concatenation in LIKE clause
            String query = "SELECT * FROM products WHERE name LIKE '%" + keyword + "%'";
            ResultSet rs = st.executeQuery(query);
            while (rs.next()) {
                results.put(new JSONObject()
                        .put("id", rs.getInt("id"))
                        .put("name", rs.getString("name"))
                        .put("price", rs.getDouble("price")));
            }
        }
        return results;
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

        server.createContext("/search", ex -> {
            if (!ex.getRequestMethod().equals("GET")) { ex.sendResponseHeaders(405, -1); return; }
            String rawQuery = ex.getRequestURI().getQuery();
            String keyword = "";
            if (rawQuery != null) {
                for (String param : rawQuery.split("&")) {
                    if (param.startsWith("q=")) keyword = java.net.URLDecoder.decode(param.substring(2), StandardCharsets.UTF_8);
                }
            }
            JSONObject resp = new JSONObject();
            int status;
            try {
                resp.put("results", searchProducts(keyword));
                status = 200;
            } catch (SQLException e) {
                resp.put("error", e.getMessage()); status = 500;
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
        return "<html><body><h2>SQL Injection Search Lab (Java)</h2></body></html>"
                .getBytes(StandardCharsets.UTF_8);
    }
}
