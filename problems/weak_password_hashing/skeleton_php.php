<?php
// WARNING: This code is intentionally vulnerable for educational purposes

$USER_STORE = [];

// VULNERABLE: MD5 is used to hash passwords.
// Fix this to use password_hash() with PASSWORD_BCRYPT and password_verify() for checking.
function hash_password($password) {
    return md5($password);
}

function verify_password($password, $stored_hash) {
    return md5($password) === $stored_hash;
}

$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

if ($request_uri === '/register' && $method === 'POST') {
    header('Content-Type: application/json');
    $data = json_decode(file_get_contents('php://input'), true);
    $username = isset($data['username']) ? trim($data['username']) : '';
    $password = isset($data['password']) ? $data['password'] : '';
    if ($username === '' || $password === '') {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'Username and password required']);
        exit;
    }
    global $USER_STORE;
    if (isset($USER_STORE[$username])) {
        http_response_code(409);
        echo json_encode(['ok' => false, 'error' => 'Username already taken']);
        exit;
    }
    $USER_STORE[$username] = hash_password($password);
    echo json_encode(['ok' => true, 'hash' => $USER_STORE[$username]]);
    exit;
}

if ($request_uri === '/login' && $method === 'POST') {
    header('Content-Type: application/json');
    $data = json_decode(file_get_contents('php://input'), true);
    $username = isset($data['username']) ? trim($data['username']) : '';
    $password = isset($data['password']) ? $data['password'] : '';
    global $USER_STORE;
    if (!isset($USER_STORE[$username])) {
        http_response_code(401);
        echo json_encode(['ok' => false, 'error' => 'Invalid credentials']);
        exit;
    }
    if (verify_password($password, $USER_STORE[$username])) {
        echo json_encode(['ok' => true, 'message' => 'Login successful']);
    } else {
        http_response_code(401);
        echo json_encode(['ok' => false, 'error' => 'Invalid credentials']);
    }
    exit;
}

if ($request_uri === '/hash' && $method === 'GET') {
    header('Content-Type: application/json');
    $user = isset($_GET['user']) ? $_GET['user'] : '';
    global $USER_STORE;
    if (!isset($USER_STORE[$user])) {
        http_response_code(404);
        echo json_encode(['error' => 'User not found']);
        exit;
    }
    echo json_encode(['hash' => $USER_STORE[$user]]);
    exit;
}

require '/app/templates/ui.php';
