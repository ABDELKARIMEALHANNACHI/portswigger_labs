<?php

function fetch($url, $referer) {

    $options = [
        "http" => [
            "header" => "Referer: $referer\r\n"
        ]
    ];

    $context = stream_context_create($options);

    return file_get_contents($url, false, $context);
}

$url = "https://vulnerable-lab.net/product";
$referer = $_GET['referer'];

echo fetch($url, $referer);

?>
