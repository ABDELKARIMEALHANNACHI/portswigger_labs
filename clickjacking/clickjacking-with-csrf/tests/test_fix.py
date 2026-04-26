#!/usr/bin/env python3
"""Tests for clickjacking-with-csrf fix.py"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fix'))

from unittest.mock import patch, MagicMock
from fix import verify, PASS

def mock_resp(headers, body=""):
    r = MagicMock(); r.headers = headers; r.text = body; return r

class TestClickjackCSRFFix:

    def test_both_protections_passes(self):
        body = '<input name="csrf" value="tok">'
        with patch("fix.requests.get") as m:
            m.return_value = mock_resp(
                {"X-Frame-Options": "DENY",
                 "Content-Security-Policy": "frame-ancestors 'none'"},
                body
            )
            c = verify("https://t.example.com")
        assert c["overall"] is True

    def test_framing_blocked_but_no_csrf_fails(self):
        with patch("fix.requests.get") as m:
            m.return_value = mock_resp({"X-Frame-Options": "DENY"}, "")
            c = verify("https://t.example.com")
        # CSRF missing → overall fails (incomplete protection)
        assert c["overall"] is False

    def test_csrf_present_but_frameable_fails(self):
        body = '<input name="csrf" value="tok">'
        with patch("fix.requests.get") as m:
            m.return_value = mock_resp({}, body)
            c = verify("https://t.example.com")
        assert c["overall"] is False
