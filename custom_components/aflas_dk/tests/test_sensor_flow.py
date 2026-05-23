from datetime import datetime
from custom_components.aflas_dk.sensor import AflasWaterFlowSensor


def test_flow_sensor(monkeypatch):
    class Coord:
        data = {
            "current": {
                "labels": [
                    "x\n(2026-05-22 00:00:00 - 2026-05-22 01:00:00)",
                    "x\n(2026-05-22 01:00:00 - 2026-05-22 02:00:00)",
                ],
                "usage": [10.0, 12.0],
            }
        }
        last_update_success = True

    sensor = AflasWaterFlowSensor(Coord(), "111")

    monkeypatch.setattr(
        "custom_components.aflas_dk.sensor.datetime",
        type("dt", (), {"fromisoformat": datetime.fromisoformat}),
    )

    assert sensor.native_value == 2.0

