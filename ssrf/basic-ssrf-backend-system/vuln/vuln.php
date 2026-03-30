<?php

if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    $stockApi = $_POST['stockApi'];

    $ch = curl_init();

    // 🚨 VULNERABLE: no validation
    curl_setopt($ch, CURLOPT_URL, $stockApi);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 2);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);

    $response = curl_exec($ch);

    if(curl_errno($ch)){
        http_response_code(500);
        echo "Request failed";
    } else {
        echo substr($response, 0, 200);
    }

    curl_close($ch);
}
?>
