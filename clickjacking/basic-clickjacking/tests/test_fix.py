#!/usr/bin/env python3
"""
Tests for basic-clickjacking/fix/fix.py
Run with: pytest tests/test_fix.py -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fix'))

from unittest.mock import patch, MagicMock
from fix import verify_fix, PASS, FAIL


def _mock_response(headers: dict):
    resp = MagicMock()
    resp.headers = headers
    return resp


class TestVerifyFix:

    def test_xfo_deny_passes(self):
        with patch("fix.requests.get") as mock_get:
            mock_get.return_value = _mock_response({"X-Frame-Options": "DENY"})
            checks = verify_fix("https://target.example.com")
        assert checks["x_frame_options"]["status"] == PASS
        assert checks["overall"] is True

    def test_xfo_sameorigin_passes(self):
        with patch("fix.requests.get") as mock_get:
            mock_get.return_value = _mock_response({"X-Frame-Options": "SAMEORIGIN"})
            checks = verify_fix("https://target.example.com")
        assert checks["x_frame_options"]["status"] == PASS

    def test_csp_frame_ancestors_none_passes(self):
        with patch("fix.requests.get") as mock_get:
            mock_get.return_value = _mock_response(
                {"Content-Security-Policy": "frame-ancestors 'none'"}
            )
            checks = verify_fix("https://target.example.com")
        assert checks["csp_frame_ancestors"]["status"] == PASS
        assert checks["overall"] is True

    def test_no_headers_fails_overall(self):
        with patch("fix.requests.get") as mock_get:
            mock_get.return_value = _mock_response({})
            checks = verify_fix("https://target.example.com")
        assert checks["overall"] is False

    def test_missing_xfo_fails(self):
        with patch("fix.requests.get") as mock_get:
            mock_get.return_value = _mock_response({})
            checks = verify_fix("https://target.example.com")
        assert checks["x_frame_options"]["status"] == FAIL
