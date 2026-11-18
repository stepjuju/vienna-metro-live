
"""Enrich train records with stable internal station IDs."""

from collections.abc import Mapping
from typing import Any

from .registry import StationRegistry


def enrich_train(
    train: Mapping[str, Any],
    stations: StationRegistry,
) -> dict[str, Any]:
    """Resolve GTFS stop IDs without modifying the original record."""

    result = dict(train)

    field_mapping = {
        "from_stop_id": "from_station_id",
        "to_stop_id": "to_station_id",
        "stop_id": "station_id",
    }

    for stop_field, station_field in field_mapping.items():
        stop_id = result.get(stop_field)

        if stop_id is not None:
            result[station_field] = stations.resolve(str(stop_id))

    return result