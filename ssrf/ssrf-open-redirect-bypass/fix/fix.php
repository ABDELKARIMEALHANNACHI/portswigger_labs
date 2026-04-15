<?php
/**
 * FIXED CODE — SSRF with Filter Bypass via Open Redirection
 * Language: PHP
 *
 * TWO BUGS FIXED:
 *
 * FIX 1 — SSRF in stock checker:
 *   a) Allowlist specific hostnames
 *   b) URL decoded before validation
 *   c) DNS resolution + private IP check
 *   d) CURLOPT_FOLLOWLOCATION=false  ← CRITICAL FIX
 *   e) Timeout enforced
 *
 * FIX 2 — Open Redirect in nextProduct:
 *   Validate path is a permitted relative URL only.
 *   Reject any absolute URL.
 */

define('APP_DOMAIN', 'your-lab-id.web-security-academy.net');

const ALLOWED_HOSTS = [
    'stock.weliketoshop.net',
    'stock.internal',
];

const BLOCKED_CIDRS = [
    '127.0.0.0/8',
    '10.0.0.0/8',
    '172.16.0.0/12',
    '192.168.0.0/16',
    '169.254.0.0/16',
];


function ip_in_cidr(string $ip, string $cidr): bool {
    [$subnet, $mask] = explode('/', $cidr);
    return (ip2long($ip) & ~((1 << (32 - (int)$mask)) - 1)) === ip2long($subnet);
}


function is_safe_url(string $url): bool {
    // Decode twice — defeats double encoding tricks
    $decoded = urldecode(urldecode($url));
    $parsed  = parse_url($decoded);

    if (!$parsed) return false;

    // HTTPS only
    if (($parsed['scheme'] ?? '') !== 'https') return false;

    $host = strtolower($parsed['host'] ?? '');
    if (!$host) return false;

    // Allowlist
    if (!in_array($host, ALLOWED_HOSTS, true)) return false;

    // DNS resolve + private IP check
    $resolved = gethostbyname($host);
    if ($resolved === $host) return false;

    foreach (BLOCKED_CIDRS as $cidr) {
        if (ip_in_cidr($resolved, $cidr)) return false;
    }

    return true;
}


// ── FIX 1: SSRF stock checker ─────────────────────────────────────────────────

function handle_stock_check(): void {
    $stockApiUrl = $_POST['stockApi'] ?? '';

    if (!$stockApiUrl) {
        http_response_code(400);
        echo json_encode(['error' => 'stockApi required']);
        return;
    }

    if (!is_safe_url($stockApiUrl)) {
        http_response_code(400);
        echo json_encode(['error' => 'URL not permitted']);
        return;
    }

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $stockApiUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    // ✅ CRITICAL FIX: FOLLOWLOCATION=false
    // Even if an open redirect exists on the allowed domain,
    // curl will NOT follow it. The chain is broken.
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);  // ✅
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);       // ✅
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);             // ✅

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    // ✅ Block redirect responses
    if ($httpCode >= 300 && $httpCode < 400) {
        http_response_code(400);
        echo json_encode(['error' => 'Redirects not permitted']);
        return;
    }

    http_response_code(200);
    header('Content-Type: application/json');
    echo json_encode(['stock' => $response]);
}


// ── FIX 2: Open Redirect nextProduct ─────────────────────────────────────────

function handle_next_product(): void {
    $path = $_GET['path'] ?? '/';

    // ✅ FIX 2: Only allow relative paths matching /product?productId=NUMBER
    // Rejects: http://..., https://..., //..., anything absolute
    if (!preg_match('/^\/product\?productId=\d+$/', $path)) {
        http_response_code(400);
        echo 'Invalid redirect destination';
        return;
    }

    header('Location: ' . $path);
    http_response_code(302);
}


/*
 * THE MINIMAL FIX — just one line stops the entire attack:
 *
 * Change:
 *   curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
 * To:
 *   curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);
 *
 * With redirect following disabled:
 *   stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin
 *   → curl fetches local path → gets 302 response
 *   → does NOT follow the redirect
 *   → returns 302 status to the application
 *   → application rejects 3xx responses
 *   → chain broken
 *
 * Still fix the open redirect too — defense in depth.
 */
?>
