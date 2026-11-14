
import csv
import os
import sqlite3
import tempfile
from io import TextIOWrapper
from pathlib import Path
from zipfile import ZipFile

from app.gtfs.loader import GTFS_PATH
from contextlib import closing

DB_PATH = GTFS_PATH.parent / "metro.db"
METRO_LINES = {"U1", "U2", "U3", "U4", "U6"}
BATCH_SIZE = 5000


def read_rows(archive: ZipFile, filename: str):
    """Stream GTFS rows without loading the whole table."""
    with (
        archive.open(filename) as file,
        TextIOWrapper(file, encoding="utf-8-sig") as text,
    ):
        yield from csv.DictReader(text)


def insert_batches(connection, query, rows):
    """Insert records in batches to reduce memory usage."""
    batch = []

    for row in rows:
        batch.append(row)

        if len(batch) >= BATCH_SIZE:
            connection.executemany(query, batch)
            batch.clear()

    if batch:
        connection.executemany(query, batch)


def create_schema(connection):
    connection.executescript("""
        CREATE TABLE routes (
            route_id TEXT PRIMARY KEY,
            line TEXT NOT NULL,
            color TEXT
        );

        CREATE TABLE trips (
            trip_id TEXT PRIMARY KEY,
            route_id TEXT NOT NULL,
            service_id TEXT NOT NULL,
            headsign TEXT,
            direction_id TEXT
        );

        CREATE TABLE stops (
            stop_id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE stop_times (
            trip_id TEXT NOT NULL,
            stop_id TEXT NOT NULL,
            sequence INTEGER NOT NULL,
            arrival TEXT NOT NULL,
            departure TEXT NOT NULL,
            PRIMARY KEY (trip_id, sequence)
        );

        CREATE TABLE calendar (
            service_id TEXT PRIMARY KEY,
            monday INTEGER,
            tuesday INTEGER,
            wednesday INTEGER,
            thursday INTEGER,
            friday INTEGER,
            saturday INTEGER,
            sunday INTEGER,
            start_date TEXT,
            end_date TEXT
        );

        CREATE TABLE calendar_dates (
            service_id TEXT NOT NULL,
            date TEXT NOT NULL,
            exception_type INTEGER NOT NULL
        );
    """)


def create_indexes(connection):
    connection.executescript("""
        CREATE INDEX idx_trips_route
            ON trips(route_id);

        CREATE INDEX idx_trips_service
            ON trips(service_id);

        CREATE INDEX idx_stop_times_stop
            ON stop_times(stop_id);

        CREATE INDEX idx_calendar_dates
            ON calendar_dates(date, service_id);
    """)


def import_gtfs(zip_path: Path, db_path: Path):
    """Import U-Bahn timetable into a new SQLite database."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    fd, temporary_name = tempfile.mkstemp(
        suffix=".db", dir=db_path.parent
    )
    os.close(fd)
    temporary_path = Path(temporary_name)

    try:
        with (
            ZipFile(zip_path) as archive,
             closing(sqlite3.connect(temporary_path)) as connection,
        ):
            create_schema(connection)

            routes = [
                row
                for row in read_rows(archive, "routes.txt")
                if row["route_short_name"] in METRO_LINES
            ]

            route_ids = {row["route_id"] for row in routes}

            insert_batches(
                connection,
                "INSERT INTO routes VALUES (?, ?, ?)",
                (
                    (
                        row["route_id"],
                        row["route_short_name"],
                        row["route_color"],
                    )
                    for row in routes
                ),
            )
            print(f"Imported {len(routes)} route records")

            trip_ids = set()
            service_ids = set()

            def metro_trips():
                for row in read_rows(archive, "trips.txt"):
                    if row["route_id"] not in route_ids:
                        continue

                    trip_ids.add(row["trip_id"])
                    service_ids.add(row["service_id"])

                    yield (
                        row["trip_id"],
                        row["route_id"],
                        row["service_id"],
                        row["trip_headsign"],
                        row["direction_id"],
                    )

            insert_batches(
                connection,
                "INSERT INTO trips VALUES (?, ?, ?, ?, ?)",
                metro_trips(),
            )
            print(f"Imported {len(trip_ids)} trips")

            insert_batches(
                connection,
                "INSERT INTO stops VALUES (?, ?)",
                (
                    (row["stop_id"], row["stop_name"])
                    for row in read_rows(archive, "stops.txt")
                ),
            )

            insert_batches(
                connection,
                "INSERT INTO stop_times VALUES (?, ?, ?, ?, ?)",
                (
                    (
                        row["trip_id"],
                        row["stop_id"],
                        int(row["stop_sequence"]),
                        row["arrival_time"],
                        row["departure_time"],
                    )
                    for row in read_rows(archive, "stop_times.txt")
                    if row["trip_id"] in trip_ids
                ),
            )
            print("Imported U-Bahn stop times")

            weekdays = (
                "monday", "tuesday", "wednesday",
                "thursday", "friday", "saturday", "sunday"
            )

            insert_batches(
                connection,
                "INSERT INTO calendar VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    (
                        row["service_id"],
                        *(int(row[day]) for day in weekdays),
                        row["start_date"],
                        row["end_date"],
                    )
                    for row in read_rows(archive, "calendar.txt")
                    if row["service_id"] in service_ids
                ),
            )

            insert_batches(
                connection,
                "INSERT INTO calendar_dates VALUES (?, ?, ?)",
                (
                    (
                        row["service_id"],
                        row["date"],
                        int(row["exception_type"]),
                    )
                    for row in read_rows(archive, "calendar_dates.txt")
                    if row["service_id"] in service_ids
                ),
            )

            create_indexes(connection)
            connection.commit()

        # Replace only after successful import and commit.
        os.replace(temporary_path, db_path)
        print(f"Database ready: {db_path}")

    finally:
        temporary_path.unlink(missing_ok=True)


if __name__ == "__main__":
    import_gtfs(GTFS_PATH, DB_PATH)
