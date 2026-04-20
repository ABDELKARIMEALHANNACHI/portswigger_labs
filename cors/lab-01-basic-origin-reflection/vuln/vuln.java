// ============================================================
// VULNERABLE CODE — Basic Origin Reflection
// DO NOT USE IN PRODUCTION
// ============================================================
const express = require('express');
const app = express();

// Simulated user database
const users = {
  sessionid_admin:  { username: 'administrator', apiKey: 'admin_secret_key_9x3f', email: 'admin@lab.net' },
  sessionid_wiener: { username: 'wiener',        apiKey: 'wiener_key_7g2k',       email: 'wiener@lab.net' }
};

// ❌ VULNERABLE endpoint — mirrors any origin blindly
app.get('/accountDetails', (req, res) => {
  const origin = req.headers['origin'];
  const session = req.cookies?.sessionid;
  const user = users[session];

  if (!user) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  // ❌ VULNERABILITY HERE:
  // Reads the Origin header and reflects it back with no validation.
  // Combined with Allow-Credentials: true, any website can read this response
  // using the victim's session cookies.
  if (origin) {
    res.setHeader('Access-Control-Allow-Origin', origin);       // ← blind mirror
    res.setHeader('Access-Control-Allow-Credentials', 'true');  // ← allows cookies
  }

  res.json({
    username: user.username,
    apiKey:   user.apiKey,
    email:    user.email
  });
});

app.listen(8080, () => console.log('Vulnerable server running on port 8080'));
