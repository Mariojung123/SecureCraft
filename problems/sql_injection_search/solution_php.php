<?php
// SECURE: uses a prepared statement with a placeholder for the LIKE query.
function get_db() {
    $db = new PDO('sqlite:/tmp/sqli_search.db');
    $db->exec("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL)");
    $db->exec("CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY, token TEXT)");
    $db->exec("INSERT OR IGNORE INTO products VALUES (1, 'Widget', 9.99)");
    $db->exec("INSERT OR IGNORE INTO products VALUES (2, 'Gadget', 19.99)");
    $db->exec("INSERT OR IGNORE INTO secrets VALUES (1, 'API_KEY_12345')");
    return $db;
}

function search_products($term) {
    $db = get_db();
    $stmt = $db->prepare("SELECT * FROM products WHERE name LIKE ?");
    $stmt->execute(['%' . $term . '%']);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

if ($request_uri === '/search' && $method === 'GET') {
    header('Content-Type: application/json');
    $term = isset($_GET['q']) ? $_GET['q'] : '';
    $rows = search_products($term);
    echo json_encode(['results' => $rows]);
    exit;
}

require '/app/templates/ui.php';
