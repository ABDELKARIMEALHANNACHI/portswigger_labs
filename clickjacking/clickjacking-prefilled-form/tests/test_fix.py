#!/usr/bin/env python3
"""Tests for prefilled-form fix.py"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fix'))

from unittest.mock import patch, MagicMock
from fix import verify, PASS

def mock_resp(headers):
    r = MagicMock(); r.headers = headers; r.text = ""; return r

class TestPrefilledFix:
    def test_xfo_sameorigin_passes(self):
        with patch("fix.requests.get") as m:
            m.return_value = mock_resp({"X-Frame-Options": "SAMEORIGIN"})
            c = verify("https://t.example.com")
        assert c["overall"] is True

    def test_no_headers_fails(self):
        with patch("fix.requests.get") as m:
            m.return_value = mock_resp({})
            c = verify("https://t.example.com")
        assert c["overall"] is False
