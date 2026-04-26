#!/usr/bin/env python3
"""Tests for multistep vuln.py — run: pytest tests/test_vuln.py -v"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'vuln'))

from unittest.mock import patch, MagicMock
from vuln import check

def mock_resp(headers, body=""):
    r = MagicMock(); r.headers = headers; r.text = body; return r

class TestMultistepVuln:
    def test_frameable_no_headers(self):
        with patch("vuln.requests.get") as m:
            m.return_value = mock_resp({})
            r = check("https://t.example.com")
        assert r["frameable"] is True

    def test_confirm_dialog_detected(self):
        with patch("vuln.requests.get") as m:
            m.return_value = mock_resp({}, "<p>Are you sure you want to delete?</p>")
            r = check("https://t.example.com")
        assert r["has_multistep_flow"] is True

    def test_xfo_deny_not_frameable(self):
        with patch("vuln.requests.get") as m:
            m.return_value = mock_resp({"X-Frame-Options": "DENY"})
            r = check("https://t.example.com")
        assert r["frameable"] is False
        assert r["vulnerable"] is False
