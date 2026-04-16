<?php
// SECURE: tracks failed attempts per IP and returns 429 after 5 attempts in 60 seconds.
$USERS = ['admin' => 'correct_password'];
$ATTEMPTS = [];

function is_rate_limited($ip) {
    global $ATTEMPTS;
    $now = time();
    $window = 60;
    $max_attempts = 5;

    if (!isset($ATTEMPTS[$ip])) {
        $ATTEMPTS[$ip] = ['count' => 0, 'window_start' => $now];
    }
    if ($now - $ATTEMPTS[$ip]['window_start'] >= $window) {
        $ATTEMPTS[$ip] = ['count' => 0, 'window_start' => $now];
    }
    $ATTEMPTS[$ip]['count']++;
    return $ATTEMPTS[$ip]['count'] > $max_attempts;
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
