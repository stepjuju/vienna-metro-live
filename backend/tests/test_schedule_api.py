
import sqlite3
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app import main
from app.gtfs.importer import create_schema
from app.gtfs.schedule import (
    get_active_services,
    get_trains_at_time,
)
from app.simulation.position import get_train_segment


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_metro.db"

    with sqlite3.connect(db_path) as connection:
        create_schema(connection)

        connection.execute(
            "INSERT INTO routes VALUES (?, ?, ?)",
            ("r1", "U1", "E3000F"),
        )

        connection.executemany(
            "INSERT INTO stops VALUES (?, ?)",
            [
                ("s1", "Station A"),
                ("s2", "Station B"),
            ],
        )

        connection.executemany(
            "INSERT INTO calendar VALUES "
            "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    "friday", 0, 0, 0, 0, 1, 0, 0,
                    "20261113", "20261114",
                ),
                (
                    "saturday", 0, 0, 0, 0, 0, 1, 0,
                    "20261113", "20261114",
                ),
            ],
        )

        connection.executemany(
            "INSERT INTO trips VALUES (?, ?, ?, ?, ?)",
            [
                ("overnight", "r1", "friday", "Station B", "0"),
                ("morning", "r1", "saturday", "Station B", "0"),
            ],
        )

        connection.executemany(
            "INSERT INTO stop_times VALUES (?, ?, ?, ?, ?)",
            [
                ("overnight", "s1", 1, "24:10:00", "24:10:00"),
                ("overnight", "s2", 2, "24:50:00", "24:50:00"),
                ("morning", "s1", 1, "00:20:00", "00:20:00"),
                ("morning", "s2", 2, "00:40:00", "00:40:00"),
            ],
        )
        connection.commit()

    monkeypatch.setattr(main, "DB_PATH", db_path)
    return db_path


def test_midnight_includes_both_service_days(test_db):
    with sqlite3.connect(test_db) as connection:
        connection.row_factory = sqlite3.Row

        trains = get_trains_at_time(
            connection,
            date(2026, 11, 14),
            "00:30:00",
            "U1",
        )

    assert len(trains) == 2

    by_id = {train["trip_id"]: train for train in trains}

    assert by_id["overnight"]["service_date"] == "2026-11-13"
    assert by_id["morning"]["service_date"] == "2026-11-14"

    assert by_id["overnight"]["progress"] == pytest.approx(0.5)
    assert by_id["morning"]["progress"] == pytest.approx(0.5)


def test_calendar_exception_cancels_service(test_db):
    with sqlite3.connect(test_db) as connection:
        connection.row_factory = sqlite3.Row

        connection.execute(
            "INSERT INTO calendar_dates VALUES (?, ?, ?)",
            ("friday", "20261113", 2),
        )
        connection.commit()

        services = get_active_services(
            connection,
            date(2026, 11, 13),
        )

    assert "friday" not in services


def test_interpolation():
    stops = [
        {
            "stop_id": "s1",
            "station": "Station A",
            "arrival": "04:59:00",
            "departure": "04:59:00",
        },
        {
            "stop_id": "s2",
            "station": "Station B",
            "arrival": "05:01:00",
            "departure": "05:01:00",
        },
    ]

    result = get_train_segment(stops, "05:00:00")

    assert result["status"] == "moving"
    assert result["progress"] == pytest.approx(0.5)
    assert result["departure"] == "04:59:00"
    assert result["arrival"] == "05:01:00"
    assert result["from_stop_id"] == "s1"
    assert result["to_stop_id"] == "s2"


def test_api_returns_overnight_trains(test_db, monkeypatch):
    class FakeStationRegistry:
        def resolve(self, stop_id: str) -> str:
            mapping = {
                "s1": "test-station-1",
                "s2": "test-station-2",
            }
            return mapping[stop_id]

    monkeypatch.setattr(
        main,
        "get_station_registry",
        lambda: FakeStationRegistry(),
    )
    client = TestClient(main.app)

    response = client.get(
        "/api/trains",
        params={
            "line": "U1",
            "date": "2026-11-14",
            "time": "00:30:00",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 2


@pytest.mark.parametrize(
    "params",
    [
        {
            "line": "U5",
            "date": "2026-11-14",
            "time": "00:30:00",
        },
        {
            "line": "U1",
            "date": "2030-01-01",
            "time": "00:30:00",
        },
        {
            "line": "U1",
            "date": "2026-11-14",
            "time": "25:00:00",
        },
    ],
)
def test_api_rejects_invalid_requests(test_db, params):
    client = TestClient(main.app)

    response = client.get("/api/trains", params=params)

    assert response.status_code == 422
