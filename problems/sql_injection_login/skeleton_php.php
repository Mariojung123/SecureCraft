<?php
// WARNING: This code is intentionally vulnerable for educational purposes

function get_db() {
    $db = new PDO('sqlite:/tmp/sqli_login.db');
    $db->exec("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)");
    $db->exec("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'supersecret123')");
    return $db;
}

// VULNERABLE: username and password are interpolated directly into the SQL query.
// Fix this to use prepared statements with placeholders.
function login($username, $password) {
    $db = get_db();
    $query = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
    $result = $db->query($query);
    return $result ? $result->fetch(PDO::FETCH_ASSOC) : null;
}

$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

if ($request_uri === '/login' && $method === 'POST') {
    header('Content-Type: application/json');
    $data = json_decode(file_get_contents('php://input'), true);
    $username = isset($data['username']) ? $data['username'] : '';
    $password = isset($data['password']) ? $data['password'] : '';
    $user = login($username, $password);
    if ($user) {
        echo json_encode(['ok' => true, 'username' => $user['username']]);
    } else {
        http_response_code(401);
        echo json_encode(['ok' => false, 'error' => 'Invalid username or password.']);
    }
    exit;
}

require '/app/templates/ui.php';
