import com.sun.net.httpserver.HttpServer;
import org.json.JSONObject;

import java.io.*;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

/**
 * SecureCraft – Command Injection (Java)
 *
 * CHALLENGE: The pingHost() method passes user input directly to a shell command.
 * An attacker can inject: host = "127.0.0.1; cat /etc/passwd"
 *
 * Fix: Pass arguments as a String[] array (no shell) instead of using Runtime.exec(String).
 */
public class skeleton_java {

    // ─── VULNERABLE method – fix this ───────────────────────────────────────────

    /**
     * VULNERABLE: hostname is interpolated into a shell command string.
     * Fix this to use ProcessBuilder with a String[] of arguments (no shell=true).
     *
     * Example fix:
     *   ProcessBuilder pb = new ProcessBuilder("ping", "-c", "1", hostname);
     *   pb.redirectErrorStream(true);
     *   Process p = pb.start();
     */
    static String pingHost(String hostname) throws IOException, InterruptedException {
        // VULNERABLE: shell=true equivalent – allows command injection via ; | & etc.
        String[] cmd = {"/bin/sh", "-c", "ping -c 1 " + hostname};
        Process proc = Runtime.getRuntime().exec(cmd);
        String output = new String(proc.getInputStream().readAllBytes(), StandardCharsets.UTF_8)
                      + new String(proc.getErrorStream().readAllBytes(), StandardCharsets.UTF_8);
        proc.waitFor();
        return output;
    }

    // ─── HTTP server boilerplate ─────────────────────────────────────────────────

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);

        server.createContext("/", ex -> {
            String path = ex.getRequestURI().getPath();

            if (path.equals("/ping") && ex.getRequestMethod().equals("GET")) {
                String rawQuery = ex.getRequestURI().getQuery();
                String host = "";
                if (rawQuery != null) {
                    for (String p : rawQuery.split("&")) {
                        if (p.startsWith("host="))
                            host = URLDecoder.decode(p.substring(5), StandardCharsets.UTF_8);
                    }
                }
                JSONObject resp = new JSONObject();
                int status;
                try {
                    resp.put("output", pingHost(host));
                    status = 200;
                } catch (Exception e) {
                    resp.put("error", e.getMessage()); status = 500;
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
        return "<html><body><h2>Command Injection Lab (Java)</h2></body></html>"
                .getBytes(StandardCharsets.UTF_8);
    }
}
