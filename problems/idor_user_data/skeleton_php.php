<?php
// WARNING: This code is intentionally vulnerable for educational purposes

$USERS = [
    1 => ['id' => 1, 'username' => 'alice', 'email' => 'alice@example.com', 'ssn' => '123-45-6789', 'balance' => 1000.0],
    2 => ['id' => 2, 'username' => 'bob',   'email' => 'bob@example.com',   'ssn' => '987-65-4321', 'balance' => 2500.0],
    3 => ['id' => 3, 'username' => 'carol', 'email' => 'carol@example.com', 'ssn' => '555-44-3333', 'balance' => 750.0],
];

// VULNERABLE: any authenticated user can access any profile by changing target_user_id.
// Fix this to compare requesting_user_id and target_user_id and return 403 if they differ.
function get_profile($requesting_user_id, $target_user_id) {
    global $USERS;
    if (!isset($USERS[$target_user_id])) {
        return [null, 'Not found'];
    }
    return [$USERS[$target_user_id], null];
}

$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

if (preg_match('#^/profile/(\d+)$#', $request_uri, $m) && $method === 'GET') {
    header('Content-Type: application/json');
    $target_user_id = (int)$m[1];
    $requesting_user_id = isset($_SERVER['HTTP_X_USER_ID']) ? (int)$_SERVER['HTTP_X_USER_ID'] : 1;
    [$user, $err] = get_profile($requesting_user_id, $target_user_id);
    if ($err !== null) {
        http_response_code($err === 'Not found' ? 404 : 403);
        echo json_encode(['error' => $err]);
        exit;
    }
    echo json_encode($user);
    exit;
}

require '/app/templates/ui.php';
