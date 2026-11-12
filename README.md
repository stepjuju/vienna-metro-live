# Vienna Metro Live

A schedule-based animated visualization of Vienna's U-Bahn network, designed for a small wall-mounted display.

## Planned features
- Import official Wiener Linien GTFS schedules
- Filter U1, U2, U3, U4 and U6 trips for the current day
- Interpolate train positions between stations on a stylized SVG diagram
- Show trains in a lightweight browser UI
- Optionally incorporate realtime departure predictions

## Stack
Python, FastAPI, pytest; planned React + TypeScript + SVG frontend.

## Backend quick start
```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
uvicorn app.main:app --reload
```
Visit http://127.0.0.1:8000/docs.

Run tests:
```powershell
pytest
```

## Data
Download official GTFS from Wiener Linien. Keep downloaded ZIP and extracted files in `data/` (ignored by Git).

## Roadmap
1. Repository and backend scaffold
2. GTFS importer + tests
3. Schedule-based position estimation
4. SVG network and train animation
5. Small-screen deployment

## Attribution
Timetable data: Wiener Linien open data (attribution required under its license). This project is independent of Wiener Linien.
