<?php
// WARNING: This code is intentionally vulnerable for educational purposes

// VULNERABLE: API key is hardcoded directly in source code.
// Fix this to read the key from an environment variable.
define('ADMIN_API_KEY', 'super_secret_admin_key_1234');

function check_api_key($provided_key) {
    return $provided_key === ADMIN_API_KEY;
}

$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

if ($request_uri === '/admin' && $method === 'GET') {
    header('Content-Type: application/json');
    $provided_key = isset($_SERVER['HTTP_X_API_KEY']) ? $_SERVER['HTTP_X_API_KEY'] : '';
    if (check_api_key($provided_key)) {
        echo json_encode([
            'ok' => true,
            'data' => 'SECRET: user_export_2024.csv, revenue=$4.2M, internal_endpoints=["/debug","/metrics"]'
        ]);
    } else {
        http_response_code(403);
        echo json_encode(['ok' => false, 'error' => 'Forbidden']);
    }
    exit;
}

require '/app/templates/ui.php';
