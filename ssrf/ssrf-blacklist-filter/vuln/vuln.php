<?php
/**
 * VULNERABLE CODE — SSRF with Blacklist-Based Input Filter
 * Language: PHP
 *
 * WHAT THIS SIMULATES:
 *   A developer patched an SSRF vulnerability with a blacklist.
 *   The blacklist does raw string matching on undecoded input.
 *   Both defenses are trivially bypassable.
 *
 * TWO DEFENSES DEPLOYED (both broken):
 *   1. Block "127.0.0.1" and "localhost" as substrings
 *   2. Block "/admin" as substring in path
 */


/**
 * Weak blacklist check.
 * ❌ No URL decoding before checking.
 * ❌ No hostname resolution before checking.
 * ❌ No normalization of alternative IP representations.
 */
function is_blocked(string $url): bool {
    $url_lower = strtolower($url);

    // ❌ DEFENSE 1 — Raw string match for IP and hostname
    // Bypassed by: 2130706433, 127.1, 0x7f000001, 0177.0.0.1, [::1]
    $blocked_hosts = ['127.0.0.1', 'localhost'];
    foreach ($blocked_hosts as $blocked) {
        if (strpos($url_lower, $blocked) !== false) {
            return true;
        }
    }

    // ❌ DEFENSE 2 — Raw string match for admin path
    // Bypassed by: /%2561dmin (double-encoded 'a')
    if (strpos($url_lower, '/admin') !== false) {
        return true;
    }

    return false;
}


$stock_api_url = $_POST['stockApi'] ?? '';

// ❌ Filter runs on raw undecoded input
if (is_blocked($stock_api_url)) {
    http_response_code(400);
    header('Content-Type: application/json');
    echo json_encode(['error' => 'External stock check service is not available']);
    exit;
}

// cURL fetches the URL — PHP's cURL library decodes %25 sequences
// /%2561dmin → /%61dmin → /admin   (decoded during HTTP request)
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $stock_api_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);  // also follows redirects — extra danger
curl_setopt($ch, CURLOPT_TIMEOUT, 10);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

http_response_code($http_code);
header('Content-Type: application/json');
echo json_encode(['stock' => $response]);


/*
 * ============================================================
 * HOW THE BYPASS WORKS AGAINST THIS CODE
 *
 * Attack flow:
 *   stockApi=http://2130706433/%2561dmin/delete?username=carlos
 *
 * 1. is_blocked() receives: "http://2130706433/%2561dmin/delete?username=carlos"
 *    - "127.0.0.1" in string? No.
 *    - "localhost" in string? No.
 *    - "/admin" in string? No (because it's /%2561dmin, not /admin).
 *    - Returns false → request PASSES the filter.
 *
 * 2. curl_init() receives the same URL.
 *    cURL resolves 2130706433 → 127.0.0.1 (loopback)
 *    cURL decodes /%2561dmin → /%61dmin → /admin
 *    cURL requests: http://127.0.0.1/admin/delete?username=carlos
 *
 * 3. Admin panel at localhost receives the request.
 *    No authentication — trusts internal requests.
 *    Deletes carlos. Returns 302.
 * ============================================================
 */
?>
