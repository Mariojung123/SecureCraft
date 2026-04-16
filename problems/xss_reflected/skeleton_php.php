<?php
// WARNING: This code is intentionally vulnerable for educational purposes

// VULNERABLE: the query parameter is echoed directly into HTML without escaping.
// Fix this to use htmlspecialchars() before rendering the value.
function search_page($query) {
    return "<html><body><h1>Results for: $query</h1></body></html>";
}

$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

if ($request_uri === '/search') {
    $query = isset($_GET['q']) ? $_GET['q'] : '';
    echo search_page($query);
    exit;
}

require '/app/templates/ui.php';
