
import json
import tempfile
import unittest
from pathlib import Path

from app.stations.enrich import enrich_train
from app.stations.registry import StationMappingError, StationRegistry


class StationRegistryTests(unittest.TestCase):

    def test_multiple_platforms_one_station(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)

            (root / "stations.json").write_text(
                json.dumps({
                    "stations": [
                        {
                            "id": "vie-schwedenplatz",
                            "display_name": "Schwedenplatz",
                            "lines": ["U1", "U4"],
                        }
                    ]
                }),
                encoding="utf-8",
            )

            (root / "mapping.json").write_text(
                json.dumps({
                    "schema_version": 1,
                    "stops": {
                        "platform-a": "vie-schwedenplatz",
                        "platform-b": "vie-schwedenplatz",
                    },
                }),
                encoding="utf-8",
            )

            registry = StationRegistry(
                root / "stations.json",
                root / "mapping.json",
            )

            self.assertEqual(
                registry.resolve("platform-a"),
                registry.resolve("platform-b"),
            )

            with self.assertRaises(StationMappingError):
                registry.resolve("unknown-platform")

    def test_stopped_train_receives_station_id(self):
        class FakeRegistry:
            def resolve(self, stop_id: str) -> str:
                return {
                    "stop-1": "vie-oberlaa",
                }[stop_id]

        train = {
            "status": "stopped",
            "station": "Oberlaa",
            "stop_id": "stop-1",
        }

        result = enrich_train(train, FakeRegistry())

        self.assertEqual(result["station_id"], "vie-oberlaa")
        self.assertEqual(result["station"], "Oberlaa")
        self.assertEqual(result["stop_id"], "stop-1")


if __name__ == "__main__":
    unittest.main()