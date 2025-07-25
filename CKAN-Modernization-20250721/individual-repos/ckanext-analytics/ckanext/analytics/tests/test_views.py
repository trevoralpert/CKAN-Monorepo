"""Tests for views.py."""

import pytest

import ckanext.analytics.validators as validators


import ckan.plugins.toolkit as tk


@pytest.mark.ckan_config("ckan.plugins", "analytics")
@pytest.mark.usefixtures("with_plugins")
def test_analytics_blueprint(app, reset_db):
    resp = app.get(tk.h.url_for("analytics.page"))
    assert resp.status_code == 200
    assert resp.body == "Hello, analytics!"
