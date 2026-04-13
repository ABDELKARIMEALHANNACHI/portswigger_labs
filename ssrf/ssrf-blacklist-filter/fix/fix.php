<?php
/**
 * FIXED CODE — SSRF with Blacklist-Based Input Filter
 * Language: PHP
 *
 * THE CORRECT APPROACH — Allowlist + DNS resolution + decode first.
 * Never use a blacklist alone.
 *
 * FIX 1 — Allowlist:        Only permit known-good hostnames.
 * FIX 2 — Decode first:     Fully decode the URL before any check.
 * FIX 3 — Resolve DNS:      Check resolved IP against private ranges.
 * FIX 4 — HTTPS only:       Reject all non-HTTPS schemes.
 * FIX 5 — No redirects:     Disable CURLOPT_FOLLOWLOCATION.
 * FIX 6 — Short timeout:    Prevent timing-based scanning.
 */


// ✅ FIX 1 — Allowlist of permitted hostnames
const ALLOWED_HOSTS = [
    'stock.weliketoshop.net',
    'stock-service.internal',
];

// Private/internal CIDR ranges to block after DNS resolution
const BLOCKED_CIDRS = [
    '127.0.0.0/8',      // loopback
    '10.0.0.0/8',       // RFC 1918
    '172.16.0.0/12',    // RFC 1918
    '192.168.0.0/16',   // RFC 1918
    '169.254.0.0/16',   // link-local (cloud metadata)
];


function ip_in_cidr(string $ip, string $cidr): bool {
    [$subnet, $mask] = explode('/', $cidr);
    $ip_long     = ip2long($ip);
    $subnet_long = ip2long($subnet);
    $mask_long   = ~((1 << (32 - (int)$mask)) - 1);
    return ($ip_long & $mask_long) === ($subnet_long & $mask_long);
}


function is_safe_url(string $url): bool {
    // ✅ FIX 2 — Decode the URL recursively before any check
    // This defeats: /%2561dmin → /%61dmin → /admin
    $decoded = $url;
    while (($next = urldecode($decoded)) !== $decoded) {
        $decoded = $next;
    }

    $parsed = parse_url($decoded);
    if (!$parsed) return false;

    // ✅ FIX 4 — HTTPS scheme only
    $scheme = strtolower($parsed['scheme'] ?? '');
    if ($scheme !== 'https') return false;

    $host = strtolower($parsed['host'] ?? '');
    if (!$host) return false;

    // ✅ FIX 1 — Exact allowlist match (checked after decoding)
    if (!in_array($host, ALLOWED_HOSTS, true)) return false;

    // ✅ FIX 3 — Resolve hostname and check against private ranges
    $resolved = gethostbyname($host);
    if ($resolved === $host) return false;  // DNS resolution failed

    foreach (BLOCKED_CIDRS as $cidr) {
        if (ip_in_cidr($resolved, $cidr)) return false;
    }

    return true;
}


$stock_api_url = $_POST['stockApi'] ?? '';

if (!$stock_api_url) {
    http_response_code(400);
    echo json_encode(['error' => 'stockApi parameter required']);
    exit;
}

// ✅ Validate before any network activity
if (!is_safe_url($stock_api_url)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid or disallowed URL']);
    exit;
}

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $stock_api_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);  // ✅ FIX 5 — no redirects
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);       // ✅ FIX 6 — short timeout
curl_setopt($ch, CURLOPT_TIMEOUT, 10);

$response  = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

// Block redirect responses at response level too
if ($http_code >= 300 && $http_code < 400) {
    http_response_code(400);
    echo json_encode(['error' => 'Redirects are not permitted']);
    exit;
}

http_response_code(200);
header('Content-Type: application/json');
echo json_encode(['stock' => $response]);
?>
