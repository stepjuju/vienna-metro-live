from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data"

GTFS_PATH = DATA_DIR / "gtfs.zip"
DB_PATH = DATA_DIR / "metro.db"