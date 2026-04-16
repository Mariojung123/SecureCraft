<?php
// WARNING: This code is intentionally vulnerable for educational purposes

// VULNERABLE: user input is concatenated directly into a shell command.
// Fix this to validate hostname and avoid shell execution with user data.
function ping_host($hostname) {
    $output = shell_exec("ping -c 1 " . $hostname);
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
