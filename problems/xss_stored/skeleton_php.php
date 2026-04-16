<?php
// WARNING: This code is intentionally vulnerable for educational purposes

function get_db() {
    $db = new PDO('sqlite:/tmp/xss_stored.db');
    $db->exec("CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, body TEXT)");
    return $db;
}

// VULNERABLE: comments are inserted into HTML without escaping.
// Fix this to apply htmlspecialchars() to each comment before rendering.
function render_comments($comments) {
    $items = '';
    foreach ($comments as $c) {
        $items .= "<li class=\"comment-item\">$c</li>";
    }
    return $items;
}

$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

if ($request_uri === '/comment' && $method === 'POST') {
    header('Content-Type: application/json');
    $data = json_decode(file_get_contents('php://input'), true);
    $body = isset($data['body']) ? $data['body'] : '';
    if ($body === '') {
        echo json_encode(['ok' => false, 'error' => 'Comment cannot be empty']);
        exit;
    }
    $db = get_db();
    $stmt = $db->prepare("INSERT INTO comments (body) VALUES (?)");
    $stmt->execute([$body]);
    echo json_encode(['ok' => true]);
    exit;
}

if ($request_uri === '/comments' && $method === 'GET') {
    header('Content-Type: application/json');
    $db = get_db();
    $rows = $db->query("SELECT body FROM comments ORDER BY id DESC")->fetchAll(PDO::FETCH_COLUMN);
    echo json_encode(['comments' => $rows]);
    exit;
}

if ($request_uri === '/render' && $method === 'POST') {
    header('Content-Type: application/json');
    $data = json_decode(file_get_contents('php://input'), true);
    $comments = isset($data['comments']) ? $data['comments'] : [];
    $html = render_comments($comments);
    echo json_encode(['html' => $html]);
    exit;
}

require '/app/templates/ui.php';
