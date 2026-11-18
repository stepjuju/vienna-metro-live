"""Build and validate GTFS stop_id -> stable schematic station ID.

Usage (project root):
    python backend/scripts/build_stop_mapping.py
    python backend/scripts/build_stop_mapping.py --db data/metro.db

Station names are matched ONLY here, during the explicit import/review step.
Unknown stops are written to shared/unmapped_stops.csv and block output.
Use shared/stop_overrides.json for ambiguous entries, keyed by GTFS stop_id.
"""
import argparse
import csv
import json
import re
import sqlite3
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARED = ROOT / 'shared'
REGISTRY = SHARED / 'stations.json'
OVERRIDES = SHARED / 'stop_overrides.json'
OUTPUT = SHARED / 'gtfs_stop_to_station.json'
UNMAPPED = SHARED / 'unmapped_stops.csv'
LINES = ('U1', 'U2', 'U3', 'U4', 'U6')

# These aliases only help generate/review the static ID mapping.
# The browser will NOT normalize station names at runtime.
ALIASES = {
    'mittelandstrasse': 'landstrasse',
    'wienmittelandstrasse': 'landstrasse',
    'wahringerstrvolksoper': 'wahringerstrassevolksoper',
    'sudtirolerplatzhauptbahnhof': 'sudtirolerplhbf',
    'sudtirolerplatzhbf': 'sudtirolerplhbf',
    'sudtirolerplhauptbahnhof': 'sudtirolerplhbf',
    'kaisermuhlenvic': 'kaisermuhlenvic',
}


def key(name: str) -> str:
    value = name.lower().replace('ß', 'ss').replace('ä', 'a').replace('ö', 'o').replace('ü', 'u')
    value = unicodedata.normalize('NFKD', value)
    value = ''.join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub('[^a-z0-9]', '', value)
    if value.startswith('wien'):
        value = value[4:]
    return ALIASES.get(value, value)


def load_registry():
    records = json.loads(REGISTRY.read_text(encoding='utf-8'))['stations']
    by_name = {}
    for station in records:
        normalized = key(station['display_name'])
        if normalized in by_name:
            raise ValueError(f'Duplicate station display name key: {normalized}')
        by_name[normalized] = station['id']
    return {s['id'] for s in records}, by_name



def read_metro_stops(db_path: Path):
    """Return unique GTFS stops used by Vienna U-Bahn trips."""

    if not db_path.is_file():
        raise FileNotFoundError(
            f"GTFS database not found: {db_path}"
        )

    # Open the existing database in read-only mode.
    db = sqlite3.connect(
        f"file:{db_path.resolve().as_posix()}?mode=ro",
        uri=True,
    )

    try:
        query = """
            SELECT DISTINCT
                s.stop_id,
                s.name
            FROM stops AS s
            JOIN stop_times AS st
                ON s.stop_id = st.stop_id
            JOIN trips AS t
                ON st.trip_id = t.trip_id
            JOIN routes AS r
                ON t.route_id = r.route_id
            WHERE r.line IN ('U1', 'U2', 'U3', 'U4', 'U6')
            ORDER BY s.stop_id
        """

        return db.execute(query).fetchall()

    finally:
        db.close()



def generate(db_path: Path):
    station_ids, names = load_registry()
    overrides = (
    json.loads(OVERRIDES.read_text(encoding="utf-8"))
    if OVERRIDES.exists()
    else {})

    stops = read_metro_stops(db_path)
    if not stops:
        raise RuntimeError('No metro stops found: check GTFS database schema/import')

    resolved = {}
    unresolved = []
    for stop_id, stop_name in stops:
        if stop_id in overrides:
            station_id = overrides[stop_id]
        else:
            station_id = names.get(key(stop_name))
        if station_id not in station_ids:
            unresolved.append((stop_id, stop_name, key(stop_name)))
        else:
            resolved[stop_id] = station_id

    # List remaining issues for review, rather than silently misplacing trains.
    with UNMAPPED.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['gtfs_stop_id', 'gtfs_stop_name', 'normalized_key'])
        writer.writerows(unresolved)

    print(f'GTFS subway stops: {len(stops)}; mapped: {len(resolved)}; unresolved: {len(unresolved)}')
    if unresolved:
        print(f'Review {UNMAPPED} and add exact stop IDs to {OVERRIDES}')
        print('Existing mapping was NOT overwritten.')
        return 1

    # Map is keyed by official stop ID, not source name.
    payload = {'schema_version': 1, 'stops': resolved}
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Validated mapping written to {OUTPUT}')
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=Path, default=ROOT / 'data' / 'metro.db')
    args = parser.parse_args()
    raise SystemExit(generate(args.db))
