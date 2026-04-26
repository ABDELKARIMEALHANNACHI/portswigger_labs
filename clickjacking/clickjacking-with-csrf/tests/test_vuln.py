#!/usr/bin/env python3
"""Tests for clickjacking-with-csrf vuln.py"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'vuln'))

from unittest.mock import patch, MagicMock
from vuln import check

def mock_resp(headers, body=""):
    r = MagicMock(); r.headers = headers; r.text = body; return r

class TestClickjackCSRF:

    def test_frameable_with_csrf_token_is_critical(self):
        body = '<input name="csrf" type="hidden" value="abc123">'
        with patch("vuln.requests.get") as m:
            m.return_value = mock_resp({}, body)
            r = check("https://t.example.com")
        assert r["has_csrf_token"] is True
        assert r["frameable"] is True
        assert r["clickjack_bypasses_csrf"] is True

    def test_frameable_no_csrf_not_critical_variant(self):
        with patch("vuln.requests.get") as m:
            m.return_value = mock_resp({}, "<form><input name='email'></form>")
            r = check("https://t.example.com")
        assert r["has_csrf_token"] is False
        assert r["clickjack_bypasses_csrf"] is False

    def test_csp_blocks_even_with_csrf_token(self):
        body = '<input name="csrf" value="abc">'
        with patch("vuln.requests.get") as m:
            m.return_value = mock_resp(
                {"Content-Security-Policy": "frame-ancestors 'none'"},
                body
            )
            r = check("https://t.example.com")
        assert r["frameable"] is False
        assert r["clickjack_bypasses_csrf"] is False

    def test_xfo_deny_blocks_even_with_csrf(self):
        body = '<input name="csrfmiddlewaretoken" value="xyz">'
        with patch("vuln.requests.get") as m:
            m.return_value = mock_resp({"X-Frame-Options": "DENY"}, body)
            r = check("https://t.example.com")
        assert r["frameable"] is False
        assert r["clickjack_bypasses_csrf"] is False
