
import sqlite3
from contextlib import closing
from datetime import date, datetime
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Query

from app.core.config import DB_PATH
from app.gtfs.schedule import get_trains_at_time

MetroLine = Literal["U1", "U2", "U3", "U4", "U6"]

TIME_PATTERN = r"^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$"

app = FastAPI(
    title="Vienna Metro Live",
    description="Schedule-based Vienna U-Bahn visualization",
    version="0.1.0",
)


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

    return {
        "line": line,
        "date": target_date.isoformat(),
        "time": current_time,
        "count": len(trains),
        "trains": trains,
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
    date_value: date = Query(alias="date"),
    time: str = Query(pattern=TIME_PATTERN),
    line: MetroLine = "U1",
):
    return query_trains(line, date_value, time)


@app.get("/api/trains/live")
def get_live_trains(line: MetroLine = "U1"):
    now = datetime.now(ZoneInfo("Europe/Vienna"))

    result = query_trains(
        line,
        now.date(),
        now.strftime("%H:%M:%S"),
    )

    return {"mode": "live", **result}
