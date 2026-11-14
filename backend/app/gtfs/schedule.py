
import sqlite3
from contextlib import closing
from datetime import date, timedelta
from time import perf_counter

from app.core.config import DB_PATH
from app.simulation.position import get_train_segment


def get_active_services(
    connection: sqlite3.Connection,
    target_date: date,
) -> set[str]:
    """Find services active on the requested date."""

    date_string = target_date.strftime("%Y%m%d")

    weekdays = (
        "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday",
    )
    weekday = weekdays[target_date.weekday()]

    # Weekday is selected from our fixed list, not user input.
    rows = connection.execute(
        f"""
        SELECT service_id
        FROM calendar
        WHERE start_date <= ?
          AND end_date >= ?
          AND {weekday} = 1
        """,
        (date_string, date_string),
    ).fetchall()

    active = {row["service_id"] for row in rows}

    exceptions = connection.execute(
        """
        SELECT service_id, exception_type
        FROM calendar_dates
        WHERE date = ?
        """,
        (date_string,),
    ).fetchall()

    for row in exceptions:
        if row["exception_type"] == 1:
            active.add(row["service_id"])
        elif row["exception_type"] == 2:
            active.discard(row["service_id"])

    return active


def get_trips_for_date(
    connection: sqlite3.Connection,
    target_date: date,
    line: str = "U1",
) -> list[sqlite3.Row]:
    """Find scheduled trips for a metro line and date."""

    services = get_active_services(connection, target_date)

    if not services:
        return []

    placeholders = ",".join("?" for _ in services)

    return connection.execute(
        f"""
        SELECT
            t.trip_id,
            t.service_id,
            t.headsign,
            t.direction_id,
            r.line
        FROM trips t
        JOIN routes r ON r.route_id = t.route_id
        WHERE r.line = ?
          AND t.service_id IN ({placeholders})
        ORDER BY t.trip_id
        """,
        (line, *sorted(services)),
    ).fetchall()


def get_trip_stops(
    connection: sqlite3.Connection,
    trip_id: str,
) -> list[sqlite3.Row]:
    """Retrieve the ordered stops for one trip."""

    return connection.execute(
        """
        SELECT
            st.stop_id,
            s.name AS station,
            st.arrival,
            st.departure,
            st.sequence
        FROM stop_times st
        JOIN stops s ON s.stop_id = st.stop_id
        WHERE st.trip_id = ?
        ORDER BY st.sequence
        """,
        (trip_id,),
    ).fetchall()



def get_active_trains(
    connection: sqlite3.Connection,
    target_date: date,
    current_time: str,
    line: str = "U1",
) -> list[dict]:
    """Return active trains using a single bulk stop-times query."""

    active_services = get_active_services(connection, target_date)

    if not active_services:
        return []

    placeholders = ",".join("?" for _ in active_services)

    query = f"""
        SELECT
            t.trip_id,
            t.headsign,
            st.stop_id,
            s.name AS station,
            st.arrival,
            st.departure,
            st.sequence
        FROM trips t
        JOIN routes r
            ON r.route_id = t.route_id
        JOIN stop_times st
            ON st.trip_id = t.trip_id
        JOIN stops s
            ON s.stop_id = st.stop_id
        WHERE r.line = ?
          AND t.service_id IN ({placeholders})
        ORDER BY t.trip_id, st.sequence
    """

    cursor = connection.execute(
        query,
        (line, *sorted(active_services)),
    )

    trains = []
    current_trip_id = None
    current_headsign = None
    trip_stops = []

    def process_trip():
        """Calculate position for the grouped trip."""
        if not trip_stops:
            return

        position = get_train_segment(trip_stops, current_time)

        if position is not None:
            trains.append({
                "trip_id": current_trip_id,
                "line": line,
                "destination": current_headsign,
                **position,
            })

    for row in cursor:
        trip_id = row["trip_id"]

        # A new trip begins: process the previous one.
        if current_trip_id is not None and trip_id != current_trip_id:
            process_trip()
            trip_stops = []

        current_trip_id = trip_id
        current_headsign = row["headsign"]

        trip_stops.append({
            "stop_id": row["stop_id"],
            "station": row["station"],
            "arrival": row["arrival"],
            "departure": row["departure"],
        })

    # Process the final trip.
    process_trip()

    return trains



def get_supported_date_range(
    connection: sqlite3.Connection,
) -> tuple[date, date]:
    """Find the available GTFS calendar date range."""

    bounds = connection.execute("""
        SELECT MIN(first_date), MAX(last_date)
        FROM (
            SELECT
                start_date AS first_date,
                end_date AS last_date
            FROM calendar

            UNION ALL

            SELECT
                date AS first_date,
                date AS last_date
            FROM calendar_dates
        )
    """).fetchone()

    if not bounds or bounds[0] is None:
        raise ValueError("No GTFS timetable is available")

    return (
        date.fromisoformat(
            f"{bounds[0][:4]}-{bounds[0][4:6]}-{bounds[0][6:]}"
        ),
        date.fromisoformat(
            f"{bounds[1][:4]}-{bounds[1][4:6]}-{bounds[1][6:]}"
        ),
    )


def get_trains_at_time(
    connection: sqlite3.Connection,
    target_date: date,
    current_time: str,
    line: str,
) -> list[dict]:
    """Include both current-day and previous-day services."""

    from app.simulation.position import time_to_seconds

    seconds = time_to_seconds(current_time)

    if not 0 <= seconds < 86400:
        raise ValueError("Expected a time between 00:00 and 23:59")

    first_date, last_date = get_supported_date_range(connection)

    if not first_date <= target_date <= last_date:
        raise ValueError(
            f"Date must be between {first_date} and {last_date}"
        )

    trains = []

    # Trips associated with the requested calendar day.
    for train in get_active_trains(
        connection,
        target_date,
        current_time,
        line,
    ):
        trains.append({
            **train,
            "service_date": target_date.isoformat(),
        })

    # Overnight trips associated with the previous service day.
    previous_date = target_date - timedelta(days=1)

    if previous_date >= first_date:
        previous_time = (
            f"{seconds // 3600 + 24:02d}:"
            f"{seconds % 3600 // 60:02d}:"
            f"{seconds % 60:02d}"
        )

        for train in get_active_trains(
            connection,
            previous_date,
            previous_time,
            line,
        ):
            trains.append({
                **train,
                "service_date": previous_date.isoformat(),
            })

    return trains


if __name__ == "__main__":
    from contextlib import closing
    from time import perf_counter

    from app.core.config import DB_PATH

    target_date = date(2026, 11, 12)
    current_time = "17:27:48"

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.row_factory = sqlite3.Row

        for line in ("U1", "U2", "U3", "U4", "U6"):
            start = perf_counter()

            trains = get_active_trains(
                connection,
                target_date,
                current_time,
                line,
            )

            elapsed_ms = (perf_counter() - start) * 1000

            print(
                f"{line}: {len(trains)} active trains, "
                f"{elapsed_ms:.2f} ms"
            )
