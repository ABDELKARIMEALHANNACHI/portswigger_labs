#!/usr/bin/env python3
"""
Tests for basic-clickjacking/vuln/vuln.py
Run with: pytest tests/test_vuln.py -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'vuln'))

from unittest.mock import patch, MagicMock
from vuln import check_clickjacking


def _mock_response(headers: dict):
    resp = MagicMock()
    resp.headers = headers
    return resp


class TestCheckClickjacking:

    def test_no_headers_is_vulnerable(self):
        with patch("vuln.requests.get") as mock_get:
            mock_get.return_value = _mock_response({})
            result = check_clickjacking("https://victim.example.com")
        assert result["vulnerable"] is True

    def test_xfo_deny_not_vulnerable(self):
        with patch("vuln.requests.get") as mock_get:
            mock_get.return_value = _mock_response({"X-Frame-Options": "DENY"})
            result = check_clickjacking("https://victim.example.com")
        assert result["vulnerable"] is False

    def test_xfo_sameorigin_not_vulnerable(self):
        with patch("vuln.requests.get") as mock_get:
            mock_get.return_value = _mock_response({"X-Frame-Options": "SAMEORIGIN"})
            result = check_clickjacking("https://victim.example.com")
        assert result["vulnerable"] is False

    def test_xfo_allow_from_is_vulnerable(self):
        with patch("vuln.requests.get") as mock_get:
            mock_get.return_value = _mock_response({"X-Frame-Options": "ALLOW-FROM https://evil.com"})
            result = check_clickjacking("https://victim.example.com")
        assert result["vulnerable"] is True

    def test_csp_frame_ancestors_none_not_vulnerable(self):
        with patch("vuln.requests.get") as mock_get:
            mock_get.return_value = _mock_response(
                {"Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'"}
            )
            result = check_clickjacking("https://victim.example.com")
        assert result["vulnerable"] is False

    def test_csp_without_frame_ancestors_vulnerable(self):
        with patch("vuln.requests.get") as mock_get:
            mock_get.return_value = _mock_response(
                {"Content-Security-Policy": "default-src 'self'"}
            )
            result = check_clickjacking("https://victim.example.com")
        assert result["vulnerable"] is True

    def test_request_exception_returns_no_vuln(self):
        import requests
        with patch("vuln.requests.get", side_effect=requests.exceptions.ConnectionError("timeout")):
            result = check_clickjacking("https://unreachable.example.com")
        assert result["vulnerable"] is False
        assert "Request failed" in result["reason"]
