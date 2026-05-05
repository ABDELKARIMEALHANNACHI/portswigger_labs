<?php

session_start();

if (
    !isset($_POST['csrf']) ||
    !hash_equals(
        $_SESSION['csrf_token'],
        $_POST['csrf']
    )
) {
    http_response_code(403);
    die();
}
