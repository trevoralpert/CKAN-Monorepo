"""Tests for helpers.py."""

import ckanext.analytics.helpers as helpers


def test_analytics_hello():
    assert helpers.analytics_hello() == "Hello, analytics!"
