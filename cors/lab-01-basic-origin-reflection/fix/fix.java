// ============================================================
// FIXED CODE — Basic Origin Reflection
// ============================================================
const express = require('express');
const app = express();

// ✅ FIX 1: Explicit whitelist — only trusted origins
const ALLOWED_ORIGINS = new Set([
  'https://trusted-app.com',
  'https://admin.trusted-app.com'
]);

app.get('/accountDetails', (req, res) => {
  const origin  = req.headers['origin'];
  const session = req.cookies?.sessionid;
  const user    = users[session];

  if (!user) return res.status(401).json({ error: 'Not authenticated' });

  // ✅ FIX 2: Only set CORS headers if origin is in the whitelist
  if (origin && ALLOWED_ORIGINS.has(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    // ✅ FIX 3: Vary header tells caches not to serve wrong CORS responses
    res.setHeader('Vary', 'Origin');
  }
  // If origin not in whitelist → no CORS headers → browser blocks the read

  res.json({
    username: user.username,
    apiKey:   user.apiKey,
    email:    user.email
  });
});

app.listen(8080);b
