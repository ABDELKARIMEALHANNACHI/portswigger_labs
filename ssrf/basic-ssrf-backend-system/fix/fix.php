<?php

function is_safe_url($url) {
    $parsed = parse_url($url);

    if (!isset($parsed['host'])) {
        return false;
    }

    $allowed = ['stock.weliketoshop.net'];

    if (!in_array($parsed['host'], $allowed)) {
        return false;
    }

    $ip = gethostbyname($parsed['host']);

    // Block internal IP ranges
    if (preg_match('/^(127\.|10\.|192\.168\.)/', $ip)) {
        return false;
    }

    return true;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    $stockApi = $_POST['stockApi'];

    if (!is_safe_url($stockApi)) {
        http_response_code(403);
        die("Blocked");
    }

    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, $stockApi);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 2);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);

    $response = curl_exec($ch);

    echo substr($response, 0, 200);

    curl_close($ch);
}
?>
