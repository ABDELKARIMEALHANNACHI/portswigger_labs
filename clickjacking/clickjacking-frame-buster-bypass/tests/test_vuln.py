#!/usr/bin/env python3
"""Tests for frame-buster-bypass vuln.py — run: pytest tests/test_vuln.py -v"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'vuln'))

from unittest.mock import patch, MagicMock
from vuln import check

def mock_resp(headers, body=""):
    r = MagicMock(); r.headers = headers; r.text = body; return r

class TestFrameBusterBypass:

    def test_frameable_no_buster(self):
        with patch("vuln.requests.get") as m:
            m.return_value = mock_resp({})
            r = check("https://t.example.com")
        assert r["frameable"] is True
        assert r["has_frame_buster_js"] is False
        assert r["sandbox_bypass_possible"] is False  # No buster = regular clickjacking, not sandbox bypass

    def test_frameable_with_buster_is_bypassable(self):
        body = "<script>if (top !== self) top.location = self.location;</script>"
        with patch("vuln.requests.get") as m:
            m.return_value = mock_resp({}, body)
            r = check("https://t.example.com")
        assert r["frameable"] is True
        assert r["has_frame_buster_js"] is True
        assert r["sandbox_bypass_possible"] is True

    def test_csp_frame_ancestors_none_not_frameable(self):
        with patch("vuln.requests.get") as m:
            m.return_value = mock_resp(
                {"Content-Security-Policy": "frame-ancestors 'none'"},
                "<script>if (top !== self) top.location = self.location;</script>"
            )
            r = check("https://t.example.com")
        assert r["frameable"] is False
        assert r["sandbox_bypass_possible"] is False

    def test_xfo_deny_not_frameable(self):
        with patch("vuln.requests.get") as m:
            m.return_value = mock_resp({"X-Frame-Options": "DENY"})
            r = check("https://t.example.com")
        assert r["frameable"] is False
