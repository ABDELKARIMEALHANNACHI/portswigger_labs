<?php
/**
 * VULNERABLE CODE — Basic SSRF Against Another Back-End System
 * Language: PHP
 *
 * WHY THIS IS VULNERABLE:
 *   $_POST['stockApi'] is passed directly to curl with no validation.
 *   The server will fetch any URL the attacker provides, including
 *   internal network addresses like http://192.168.0.X:8080/admin.
 */

// ❌ VULNERABLE: No validation on user-supplied URL
$stockApiUrl = $_POST['stockApi'];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $stockApiUrl);       // attacker controls this
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);    // follows redirects — makes chaining easier
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

http_response_code($httpCode);
header('Content-Type: application/json');
echo json_encode(['stock' => $response]);


/*
 * ============================================================
 * HOW THE ATTACK WORKS AGAINST THIS CODE
 *
 * Normal:
 *   stockApi=https://stock.internal/product/123
 *
 * Attack — scan internal network:
 *   stockApi=http://192.168.0.1:8080/admin   (1 through 255)
 *   One IP returns 200 + admin HTML
 *
 * Attack — delete user:
 *   stockApi=http://192.168.0.68:8080/admin/delete?username=carlos
 *
 * Extra danger: CURLOPT_FOLLOWLOCATION=true means an attacker
 * can use an open redirect on any allowed domain to bypass
 * future URL validation:
 *   stockApi=https://allowed.com/redirect?url=http://192.168.0.68:8080/admin
 * ============================================================
 */
?><?php

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
