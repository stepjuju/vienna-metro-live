
import logging
import sqlite3
from contextlib import closing
from datetime import date, datetime
from functools import lru_cache
from typing import Annotated, Literal
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Query

from app.core.config import DB_PATH
from app.gtfs.schedule import get_trains_at_time
from app.stations.enrich import enrich_train
from app.stations.registry import (
    StationMappingError,
    StationRegistry,
)

MetroLine = Literal["U1", "U2", "U3", "U4", "U6"]
LineParam = Annotated[MetroLine, Query()]

TIME_PATTERN = r"^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$"

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Vienna Metro Live",
    description="Schedule-based Vienna U-Bahn visualization",
    version="0.1.0",
)


@lru_cache(maxsize=1)
def get_station_registry() -> StationRegistry:
    """Load the validated stop-ID mapping once per process."""
    return StationRegistry()


def query_trains(
    line: MetroLine,
    target_date: date,
    current_time: str,
) -> dict:
    try:
        with closing(sqlite3.connect(DB_PATH)) as connection:
            connection.row_factory = sqlite3.Row

            trains = get_trains_at_time(
                connection,
                target_date,
                current_time,
                line,
            )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    try:
        registry = get_station_registry()

        enriched_trains = [
            enrich_train(train, registry)
            for train in trains
        ]

    except (StationMappingError, OSError, ValueError, KeyError) as exc:
        logger.exception(
            "Station mapping failed for line %s", line
        )

        raise HTTPException(
            status_code=503,
            detail="Station mapping is unavailable or incomplete.",
        ) from exc

    return {
        "line": line,
        "date": target_date.isoformat(),
        "time": current_time,
        "count": len(enriched_trains),
        "trains": enriched_trains,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/lines")
def get_lines():
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute("""
            SELECT line, MIN(color) AS color
            FROM routes
            GROUP BY line
            ORDER BY line
        """).fetchall()

    return [
        {
            "line": row["line"],
            "color": f"#{row['color']}",
        }
        for row in rows
    ]


@app.get("/api/trains")
def get_trains(
    date_value: Annotated[date, Query(alias="date")],
    time: str = Query(pattern=TIME_PATTERN),
    line: MetroLine = "U1",
):
    return query_trains(line, date_value, time)


@app.get("/api/trains/live")
def get_live_trains(line: LineParam = "U1"):
    now = datetime.now(ZoneInfo("Europe/Vienna"))

    result = query_trains(
        line,
        now.date(),
        now.strftime("%H:%M:%S"),
    )

    return {"mode": "live", **result}
