import csv
from functools import lru_cache
from io import TextIOWrapper
from pathlib import Path
from zipfile import ZipFile

GTFS_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "gtfs.zip"
)


@lru_cache(maxsize=8)
def load_gtfs_table(filename: str) -> list[dict[str, str]]:
    """Load each GTFS table once and cache it in memory."""

    with (
        ZipFile(GTFS_PATH) as archive,
        archive.open(filename) as file,
        TextIOWrapper(file, encoding="utf-8-sig") as text_file,
    ):
        reader = csv.DictReader(text_file)
        return list(reader)
