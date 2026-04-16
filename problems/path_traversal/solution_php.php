<?php
// SECURE: uses realpath() to resolve the path and verifies it stays within BASE_DIR.
define('BASE_DIR', '/app/files');

function get_file($filename) {
    $base = realpath(BASE_DIR);
    $path = realpath(BASE_DIR . '/' . $filename);
    if ($path === false || strpos($path, $base . DIRECTORY_SEPARATOR) !== 0) {
        return [null, 'Access denied'];
    }
    if (!file_exists($path)) {
        return [null, 'Not found'];
    }
    return [file_get_contents($path), null];
}

$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

if (!is_dir(BASE_DIR)) { @mkdir(BASE_DIR, 0755, true); }
if (!file_exists(BASE_DIR . '/public.txt')) {
    file_put_contents(BASE_DIR . '/public.txt', "This is a public file.\nSafe to read.\n");
}

if ($request_uri === '/download' && $method === 'GET') {
    $filename = isset($_GET['file']) ? $_GET['file'] : '';
    if ($filename === '') {
        http_response_code(400);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'file parameter required']);
        exit;
    }
    [$content, $err] = get_file($filename);
    if ($err !== null) {
        http_response_code($err === 'Not found' ? 404 : 403);
        header('Content-Type: application/json');
        echo json_encode(['error' => $err]);
        exit;
    }
    header('Content-Type: text/plain');
    echo $content;
    exit;
}

require '/app/templates/ui.php';
