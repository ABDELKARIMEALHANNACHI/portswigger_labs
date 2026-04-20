// ============================================================
// VULNERABLE CODE — Trusted Insecure Protocols
// DO NOT USE IN PRODUCTION
// ============================================================
const express = require('express');
const app     = express();

// ❌ VULNERABILITY 1: Regex matches any subdomain — including HTTP ones
// Developer intended to whitelist only trusted subdomains but:
//   - Allows HTTP (not just HTTPS) → MITM injection possible in real world
//   - Any subdomain is trusted → one XSS = full bypass
const ORIGIN_REGEX = /^https?:\/\/([a-z0-9-]+\.)?lab-id\.web-security-academy\.net$/;
//                    ^^^^^^^^
//                    http OR https — this is the mistake

app.get('/accountDetails', (req, res) => {
  const origin  = req.headers['origin'];
  const session = req.cookies?.sessionid;
  const user    = users[session];

  if (!user) return res.status(401).json({ error: 'Not authenticated' });

  if (origin && ORIGIN_REGEX.test(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.setHeader('Vary', 'Origin');
  }

  res.json({ username: user.username, apiKey: user.apiKey, email: user.email });
});


// ❌ VULNERABILITY 2: XSS on stock subdomain — productId is reflected unsanitized
// Running on http://stock.lab-id.web-security-academy.net
app.get('/', (req, res) => {
  const productId = req.query.productId; // ← unsanitized user input
  const storeId   = req.query.storeId;

  // ❌ productId injected directly into HTML — classic reflected XSS
  res.send(`
    <html>
      <body>
        <h1>Stock Check</h1>
        <p>Checking stock for product: ${productId}</p>
        <!-- ^ if productId = 4<script>alert(1)</script> → XSS fires -->
      </body>
    </html>
  `);
});

app.listen(8080);
