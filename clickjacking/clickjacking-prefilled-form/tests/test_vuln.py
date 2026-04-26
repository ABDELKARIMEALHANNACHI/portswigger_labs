#!/usr/bin/env python3
"""Tests for prefilled-form vuln.py"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'vuln'))

from unittest.mock import patch, MagicMock
from vuln import check, SENTINEL

def mock_resp(headers, body=""):
    r = MagicMock(); r.headers = headers; r.text = body; return r

class TestPrefilledVuln:

    def test_reflected_param_and_frameable(self):
        body = f'<input type="email" value="{SENTINEL}">'
        with patch("vuln.requests.get") as m:
            m.return_value = mock_resp({}, body)
            r = check("https://t.example.com")
        assert r["frameable"] is True
        assert r["param_reflected_in_form"] is True
        assert r["vulnerable"] is True

    def test_frameable_but_not_reflected(self):
        with patch("vuln.requests.get") as m:
            m.return_value = mock_resp({}, "<input type='email' value=''>")
            r = check("https://t.example.com")
        assert r["param_reflected_in_form"] is False
        assert r["vulnerable"] is False

    def test_reflected_but_not_frameable(self):
        body = f'<input value="{SENTINEL}">'
        with patch("vuln.requests.get") as m:
            m.return_value = mock_resp({"X-Frame-Options": "DENY"}, body)
            r = check("https://t.example.com")
        assert r["frameable"] is False
        assert r["vulnerable"] is False
