<?php
// WARNING: This code is intentionally vulnerable for educational purposes

define('BASE_DIR', '/app/files');

// VULNERABLE: filename is joined to BASE_DIR without checking whether
// the result escapes the base directory.
// Fix this to use realpath() and verify the path starts with BASE_DIR.
function get_file($filename) {
    $path = BASE_DIR . '/' . $filename;
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
        http_response_code(404);
        header('Content-Type: application/json');
        echo json_encode(['error' => $err]);
        exit;
    }
    header('Content-Type: text/plain');
    echo $content;
    exit;
}

require '/app/templates/ui.php';
