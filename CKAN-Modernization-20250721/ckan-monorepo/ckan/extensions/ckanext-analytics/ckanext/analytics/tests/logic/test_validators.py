"""Tests for validators.py."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.analytics.logic import validators


def test_analytics_reauired_with_valid_value():
    assert validators.analytics_required("value") == "value"


def test_analytics_reauired_with_invalid_value():
    with pytest.raises(tk.Invalid):
        validators.analytics_required(None)
