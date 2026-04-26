#!/usr/bin/env python3
"""Tests for frame-buster-bypass fix.py — run: pytest tests/test_fix.py -v"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fix'))

from unittest.mock import patch, MagicMock
from fix import verify, PASS, FAIL

def mock_resp(headers, body=""):
    r = MagicMock(); r.headers = headers; r.text = body; return r

class TestFrameBusterFix:

    def test_csp_passes_overall(self):
        with patch("fix.requests.get") as m:
            m.return_value = mock_resp({"Content-Security-Policy": "frame-ancestors 'none'"})
            c = verify("https://t.example.com")
        assert c["csp_frame_ancestors"]["status"] == PASS
        assert c["overall"] is True

    def test_no_headers_fails(self):
        with patch("fix.requests.get") as m:
            m.return_value = mock_resp({})
            c = verify("https://t.example.com")
        assert c["overall"] is False

    def test_js_buster_without_csp_warns(self):
        body = "<script>if (top !== self) top.location = self.location;</script>"
        with patch("fix.requests.get") as m:
            m.return_value = mock_resp({}, body)
            c = verify("https://t.example.com")
        assert "sandbox bypass still possible" in c["js_buster_only"]["detail"]
