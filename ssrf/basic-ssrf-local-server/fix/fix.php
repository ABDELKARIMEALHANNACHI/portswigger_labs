<?php

function is_valid_url($url) {
    $parsed = parse_url($url);

    if (!isset($parsed['host'])) {
        return false;
    }

    $allowed_hosts = ['stock.weliketoshop.net'];

    // 🚨 Allowlist check
    if (!in_array($parsed['host'], $allowed_hosts)) {
        return false;
    }

    // 🚨 Block localhost
    if ($parsed['host'] === 'localhost' || $parsed['host'] === '127.0.0.1') {
        return false;
    }

    return true;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    $stockApi = $_POST['stockApi'];

    // 🚨 Validate BEFORE making request
    if (!is_valid_url($stockApi)) {
        die("Blocked: Invalid URL");
    }

    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, $stockApi);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false); // 🚨 safer: disable redirects

    $response = curl_exec($ch);

    if(curl_errno($ch)){
        echo "Error: " . curl_error($ch);
    } else {
        echo $response;
    }

    curl_close($ch);
}
?>
