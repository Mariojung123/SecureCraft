<?php
// WARNING: This code is intentionally vulnerable for educational purposes

$USERS = ['admin' => 'correct_password'];

// VULNERABLE: no rate limiting — infinite brute-force attempts allowed.
// Fix this to track attempts per IP and return 429 after 5 attempts in 60 seconds.
function is_rate_limited($ip) {
    return false; // TODO: implement rate limiting
}

$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

if ($request_uri === '/login' && $method === 'POST') {
    header('Content-Type: application/json');
    $ip = isset($_SERVER['HTTP_X_FORWARDED_FOR']) ? $_SERVER['HTTP_X_FORWARDED_FOR'] : $_SERVER['REMOTE_ADDR'];
    if (is_rate_limited($ip)) {
        http_response_code(429);
        echo json_encode(['error' => 'Too many requests']);
        exit;
    }
    $data = json_decode(file_get_contents('php://input'), true);
    $username = isset($data['username']) ? $data['username'] : '';
    $password = isset($data['password']) ? $data['password'] : '';
    global $USERS;
    if (isset($USERS[$username]) && $USERS[$username] === $password) {
        echo json_encode(['ok' => true, 'message' => 'Login successful']);
    } else {
        http_response_code(401);
        echo json_encode(['ok' => false, 'error' => 'Invalid credentials']);
    }
    exit;
}

require '/app/templates/ui.php';
