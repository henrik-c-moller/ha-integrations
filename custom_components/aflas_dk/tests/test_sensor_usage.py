from datetime import datetime
from custom_components.aflas_dk.sensor import AflasWaterUsageSensor


def test_usage_sensor_extracts_today(monkeypatch):
    class Coord:
        data = {
            "current": {
                "labels": [
                    "x\n(2026-05-21 00:00:00 - 2026-05-22 00:00:00)",
                    "x\n(2026-05-22 00:00:00 - 2026-05-23 00:00:00)",
                ],
                "usage": [1.0, 2.0],
            }
        }
        last_update_success = True

    sensor = AflasWaterUsageSensor(Coord(), "111")

    monkeypatch.setattr(
        "custom_components.aflas_dk.sensor.datetime",
        type("dt", (), {"now": lambda: datetime(2026, 5, 23), "fromisoformat": datetime.fromisoformat}),
    )

    assert sensor.native_value == 2.0

