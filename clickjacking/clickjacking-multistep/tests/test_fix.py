#!/usr/bin/env python3
"""Tests for multistep fix.py — run: pytest tests/test_fix.py -v"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fix'))

from unittest.mock import patch, MagicMock
from fix import verify, PASS

def mock_resp(headers):
    r = MagicMock(); r.headers = headers; r.text = ""; return r

class TestMultistepFix:
    def test_xfo_passes(self):
        with patch("fix.requests.get") as m:
            m.return_value = mock_resp({"X-Frame-Options": "DENY"})
            c = verify("https://t.example.com")
        assert c["overall"] is True

    def test_csp_passes(self):
        with patch("fix.requests.get") as m:
            m.return_value = mock_resp({"Content-Security-Policy": "frame-ancestors 'none'"})
            c = verify("https://t.example.com")
        assert c["overall"] is True

    def test_no_headers_fails(self):
        with patch("fix.requests.get") as m:
            m.return_value = mock_resp({})
            c = verify("https://t.example.com")
        assert c["overall"] is False
