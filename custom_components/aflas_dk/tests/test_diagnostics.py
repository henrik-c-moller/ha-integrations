import pytest
from unittest.mock import MagicMock

from custom_components.aflas_dk.diagnostics import (
    async_get_config_entry_diagnostics,
)


@pytest.mark.asyncio
async def test_diagnostics_basic_structure(hass):
    """Ensure diagnostics returns the expected structure."""

    # Fake config entry
    entry = MagicMock()
    entry.entry_id = "test123"
    entry.title = "Aflas Test"
    entry.data = {
        "username": "u",
        "password": "p",
        "vaerknummer": "1234",
    }
    entry.options = {"update_interval": 60}

    # Fake coordinator
    class FakeCoordinator:
        last_update_success = True
        update_interval = "60 minutes"
        _normal_interval = "60 minutes"
        _failure_count = 0
        data = {"current": {"labels": ["x"], "usage": [1.0]}}

    # Inject into hass.data
    hass.data.setdefault("aflas_dk", {})
    hass.data["aflas_dk"][entry.entry_id] = {
        "coordinators": {
            "111": FakeCoordinator(),
            "222": FakeCoordinator(),
        }
    }

    result = await async_get_config_entry_diagnostics(hass, entry)

    # Top-level keys
    assert "config_entry" in result
    assert "meters" in result

    # Config entry section
    assert result["config_entry"]["title"] == "Aflas Test"
    assert result["config_entry"]["data"]["vaerknummer"] == "1234"
    assert result["config_entry"]["options"]["update_interval"] == 60

    # Meter diagnostics
    assert "111" in result["meters"]
    assert "222" in result["meters"]

    meter_diag = result["meters"]["111"]

    assert meter_diag["last_update_success"] is True
    assert meter_diag["failure_count"] == 0
    assert meter_diag["last_data"]["current"]["usage"] == [1.0]


@pytest.mark.asyncio
async def test_diagnostics_failure_count(hass):
    """Ensure diagnostics exposes failure counters."""

    entry = MagicMock()
    entry.entry_id = "test456"
    entry.title = "Aflas Test 2"
    entry.data = {"username": "u", "password": "p", "vaerknummer": "5678"}
    entry.options = {"update_interval": 30}

    class FakeCoordinator:
        last_update_success = False
        update_interval = "10 minutes"
        _normal_interval = "30 minutes"
        _failure_count = 3
        data = {"current": {"labels": ["a", "b"], "usage": [5.0, 7.0]}}

    hass.data.setdefault("aflas_dk", {})
    hass.data["aflas_dk"][entry.entry_id] = {
        "coordinators": {"999": FakeCoordinator()}
    }

    result = await async_get_config_entry_diagnostics(hass, entry)

    meter_diag = result["meters"]["999"]

    assert meter_diag["failure_count"] == 3
    assert meter_diag["last_update_success"] is False
    assert meter_diag["last_data"]["current"]["usage"] == [5.0, 7.0]

