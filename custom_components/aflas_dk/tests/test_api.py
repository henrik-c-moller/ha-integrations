import pytest
from unittest.mock import MagicMock
from custom_components.aflas_dk.api import AflasAPI


def test_validate_login_success(monkeypatch):
    api = AflasAPI("u", "p", "1234")

    login_resp = MagicMock()
    login_resp.status_code = 302

    settings_resp = MagicMock()
    settings_resp.status_code = 200
    settings_resp.json.return_value = {"maalerNr": ["111"]}

    monkeypatch.setattr(api, "login", lambda: login_resp)
    monkeypatch.setattr(api, "get_settings", lambda: settings_resp)

    assert api.validate_login() is True


def test_validate_login_invalid(monkeypatch):
    api = AflasAPI("u", "p", "1234")

    login_resp = MagicMock()
    login_resp.status_code = 200

    monkeypatch.setattr(api, "login", lambda: login_resp)

    assert api.validate_login() == "invalid_auth"


def test_get_current_usage_missing_field(monkeypatch):
    api = AflasAPI("u", "p", "1234", "111")

    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {}

    monkeypatch.setattr(api.session, "get", lambda *a, **k: resp)

    with pytest.raises(Exception):
        api.get_current_usage()
