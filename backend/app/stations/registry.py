"""Read the reviewed ID mapping; never match by stop name at request time."""
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = PROJECT_ROOT / 'shared' / 'stations.json'
MAPPING_PATH = PROJECT_ROOT / 'shared' / 'gtfs_stop_to_station.json'


class StationMappingError(ValueError):
    pass


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


class StationRegistry:
    def __init__(self, registry_path: Path = REGISTRY_PATH,
                 mapping_path: Path = MAPPING_PATH):
        source = read_json(registry_path)
        self.stations = {station['id']: station for station in source['stations']}
        if len(self.stations) != len(source['stations']):
            raise StationMappingError('Duplicate internal station IDs')
        mapping = read_json(mapping_path)
        if mapping.get('schema_version') != 1:
            raise StationMappingError('Unsupported stop-mapping schema version')
        self.stop_to_station: dict[str, str] = mapping['stops']
        invalid = {stop: sid for stop, sid in self.stop_to_station.items()
                   if sid not in self.stations}
        if invalid:
            raise StationMappingError(f'Mappings reference missing stations: {invalid}')

    def resolve(self, gtfs_stop_id: str) -> str:
        try:
            return self.stop_to_station[gtfs_stop_id]
        except KeyError as error:
            raise StationMappingError(f'Unknown GTFS stop ID: {gtfs_stop_id}') from error

    def station(self, station_id: str) -> dict:
        return self.stations[station_id]
