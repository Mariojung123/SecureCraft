<?php
// SECURE: query parameter is escaped with htmlspecialchars() before rendering.
function search_page($query) {
    $safe = htmlspecialchars($query, ENT_QUOTES, 'UTF-8');
    return "<html><body><h1>Results for: $safe</h1></body></html>";
}

$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

if ($request_uri === '/search') {
    $query = isset($_GET['q']) ? $_GET['q'] : '';
    echo search_page($query);
    exit;
}

require '/app/templates/ui.php';
