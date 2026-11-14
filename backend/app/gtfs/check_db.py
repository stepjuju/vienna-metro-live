
import sqlite3
from contextlib import closing

from app.gtfs.importer import DB_PATH

with closing(sqlite3.connect(DB_PATH)) as connection:
    tables = [
        "routes",
        "trips",
        "stops",
        "stop_times",
        "calendar",
        "calendar_dates",
    ]

    for table in tables:
        count = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(f"{table}: {count:,}")

    print("\nTrips by metro line:")

    rows = connection.execute("""
    SELECT DISTINCT
        r.line,
        s.name,
        s.stop_id
    FROM stops s
    JOIN stop_times st ON st.stop_id = s.stop_id
    JOIN trips t ON t.trip_id = st.trip_id
    JOIN routes r ON r.route_id = t.route_id
    WHERE s.name LIKE '%Schwedenplatz%'
    ORDER BY r.line, s.stop_id
""").fetchall()

for line, name, stop_id in rows:
    print(f"{line} | {name} | {stop_id}")
