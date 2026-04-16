<?php
// SECURE: validates hostname against a strict allowlist pattern before executing.
function ping_host($hostname) {
    if (!preg_match('/^[a-zA-Z0-9.\-]+$/', $hostname)) {
        return "Error: invalid hostname";
    }
    $output = shell_exec("ping -c 1 " . escapeshellarg($hostname));
    return $output ? $output : "No output";
}

$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

if ($request_uri === '/ping' && ($method === 'POST' || $method === 'GET')) {
    header('Content-Type: application/json');
    if ($method === 'GET') {
        $hostname = isset($_GET['host']) ? $_GET['host'] : '';
    } else {
        $data = json_decode(file_get_contents('php://input'), true);
        $hostname = isset($data['hostname']) ? $data['hostname'] : '';
    }
    if ($hostname === '') {
        echo json_encode(['error' => 'hostname required']);
        exit;
    }
    $result = ping_host($hostname);
    echo json_encode(['output' => $result]);
    exit;
}

require '/app/templates/ui.php';
