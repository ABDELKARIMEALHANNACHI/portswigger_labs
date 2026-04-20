// ============================================================
// FIXED CODE — Trusted Insecure Protocols
// ============================================================
const express  = require('express');
const escape   = require('lodash/escape'); // for XSS fix
const app      = express();

// ✅ FIX 1: Only trust HTTPS subdomains — no HTTP allowed
const ORIGIN_REGEX = /^https:\/\/([a-z0-9-]+\.)?trusted-site\.com$/;
//                    ^^^^^^^
//                    https only — no ? after s

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

  res.json({ username: user.username, apiKey: user.apiKey });
});


// ✅ FIX 2: Sanitize productId to prevent XSS on stock subdomain
app.get('/', (req, res) => {
  const productId = escape(req.query.productId ?? '');
  //                ^^^^^^
  //                HTML-encodes < > " ' & → XSS impossible

  res.send(`
    <html>
      <body>
        <h1>Stock Check</h1>
        <p>Product: ${productId}</p>
      </body>
    </html>
  `);
});

app.listen(8080);
