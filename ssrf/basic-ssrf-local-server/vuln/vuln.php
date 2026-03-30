<?php

if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    $stockApi = $_POST['stockApi'];

    // 🚨 VULNERABLE: direct user-controlled URL
    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, $stockApi);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true); // 🔥 makes it worse (redirect SSRF)

    $response = curl_exec($ch);

    if(curl_errno($ch)){
        echo "Error: " . curl_error($ch);
    } else {
        echo $response;
    }

    curl_close($ch);
}
?>

<form method="POST">
    <input type="text" name="stockApi" placeholder="Enter stock API URL">
    <button type="submit">Check Stock</button>
</form>
