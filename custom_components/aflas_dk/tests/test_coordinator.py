import pytest
from unittest.mock import MagicMock
from datetime import timedelta

from custom_components.aflas_dk.coordinator import AflasCoordinator


@pytest.mark.asyncio
async def test_coordinator_success(hass):
    entry = MagicMock()
    entry.data = {"username": "u", "password": "p", "vaerknummer": "1234"}

    api_mock = MagicMock()
    api_mock.get_usage_data.return_value = {"current": {"labels": [], "usage": []}}

    with pytest.patch(
        "custom_components.aflas_dk.coordinator.AflasAPI", return_value=api_mock
    ):
        coord = AflasCoordinator(hass, entry, "111", update_interval_minutes=60)
        result = await coord._async_update_data()

        assert result["current"] == {"labels": [], "usage": []}
        assert coord.update_interval == timedelta(minutes=60)
        assert coord._failure_count == 0


@pytest.mark.asyncio
async def test_coordinator_backoff(hass):
    entry = MagicMock()
    entry.data = {"username": "u", "password": "p", "vaerknummer": "1234"}

    api_mock = MagicMock()
    api_mock.get_usage_data.side_effect = Exception("fail")

    with pytest.patch(
        "custom_components.aflas_dk.coordinator.AflasAPI", return_value=api_mock
    ):
        coord = AflasCoordinator(hass, entry, "111", update_interval_minutes=60)

        with pytest.raises(Exception):
            await coord._async_update_data()

        assert coord._failure_count == 1
        assert coord.update_interval == timedelta(minutes=5)

