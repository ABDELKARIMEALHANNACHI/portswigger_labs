<?php
/**
 * FIXED CODE — Basic SSRF Against Another Back-End System
 * Language: PHP
 *
 * FIXES APPLIED:
 *   1. Allowlist — only known stock service hostname permitted
 *   2. DNS resolution check — resolved IP must not be internal/private
 *   3. Scheme enforcement — HTTPS only
 *   4. Redirects disabled — blocks open-redirect bypass chains
 *   5. Timeout enforced — prevents hanging on internal slow services
 */

// ✅ FIX 1 — Allowlist of permitted hostnames
const ALLOWED_HOSTS = [
    'stock.internal',
    'stock-service.production.internal',
];

// ✅ FIX 2 — Private/internal CIDR ranges to block
const BLOCKED_CIDRS = [
    '127.0.0.0/8',       // loopback
    '10.0.0.0/8',        // private
    '172.16.0.0/12',     // private
    '192.168.0.0/16',    // private
    '169.254.0.0/16',    // link-local (cloud metadata)
];


function ip_in_cidr(string $ip, string $cidr): bool {
    [$subnet, $mask] = explode('/', $cidr);
    return (ip2long($ip) & ~((1 << (32 - (int)$mask)) - 1)) === ip2long($subnet);
}


function is_safe_url(string $url): bool {
    $parsed = parse_url($url);
    if (!$parsed) return false;

    // ✅ FIX 3 — HTTPS only
    if (($parsed['scheme'] ?? '') !== 'https') return false;

    $host = $parsed['host'] ?? '';
    if (!$host) return false;

    // ✅ FIX 1 — Must be on the allowlist
    if (!in_array($host, ALLOWED_HOSTS, true)) return false;

    // ✅ FIX 2 — Resolve and verify the IP is not internal
    $resolved = gethostbyname($host);
    if ($resolved === $host) return false;  // DNS resolution failed

    foreach (BLOCKED_CIDRS as $cidr) {
        if (ip_in_cidr($resolved, $cidr)) return false;
    }

    return true;
}


$stockApiUrl = $_POST['stockApi'] ?? '';

if (!$stockApiUrl) {
    http_response_code(400);
    echo json_encode(['error' => 'stockApi parameter required']);
    exit;
}

// ✅ Validate before fetching
if (!is_safe_url($stockApiUrl)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid or disallowed URL']);
    exit;
}

// ✅ FIX 4 — Disable redirect following
// ✅ FIX 5 — Enforce connection and response timeout
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $stockApiUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);  // ✅ no redirects
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);       // ✅ 5s connect timeout
curl_setopt($ch, CURLOPT_TIMEOUT, 10);             // ✅ 10s total timeout

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

// ✅ Block redirects at response level too
if ($httpCode >= 300 && $httpCode < 400) {
    http_response_code(400);
    echo json_encode(['error' => 'Redirects are not permitted']);
    exit;
}

http_response_code(200);
header('Content-Type: application/json');
echo json_encode(['stock' => $response]);
?>
