<?php

$ALLOWED_HOSTS = ["vulnerable-lab.net"];

function isAllowed($url) {
    global $ALLOWED_HOSTS;

    $parsed = parse_url($url);

    if (!isset($parsed['host'])) {
        return false;
    }

    return in_array($parsed['host'], $ALLOWED_HOSTS);
}

function fetch($url, $referer) {

    // 🔒 BLOCK SSRF BEFORE REQUEST
    if (!isAllowed($url)) {
        die("Blocked: unauthorized host");
    }

    // validate referer too
    if ($referer) {
        $ref = parse_url($referer);

        if (!isset($ref['host']) || !in_array($ref['host'], $GLOBALS['ALLOWED_HOSTS'])) {
            die("Blocked: invalid referer");
        }
    }

    $options = [
        "http" => [
            "header" => "Referer: $referer\r\n",
            "timeout" => 3
        ]
    ];

    $context = stream_context_create($options);

    return file_get_contents($url, false, $context);
}

$url = "https://vulnerable-lab.net/product";
$referer = $_GET['referer'] ?? '';

echo fetch($url, $referer);

?>
