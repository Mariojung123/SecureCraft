<?php
// SECURE: API key is read from an environment variable, not hardcoded.
function get_admin_api_key() {
    return getenv('ADMIN_API_KEY') ?: '';
}

function check_api_key($provided_key) {
    $expected = get_admin_api_key();
    if ($expected === '') {
        return false;
    }
    return hash_equals($expected, $provided_key);
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
