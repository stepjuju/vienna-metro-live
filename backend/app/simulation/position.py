"""Estimate a train's position between diagram points."""


def interpolate_position(
    start: tuple[float, float],
    end: tuple[float, float],
    departure_seconds: float,
    arrival_seconds: float,
    current_seconds: float,
) -> tuple[float, float]:
    """Linearly interpolate a position, clamping before departure/after arrival.

    Times are seconds on a common service-day timeline.
    """
    if arrival_seconds <= departure_seconds:
        raise ValueError("arrival_seconds must be after departure_seconds")
    fraction = (current_seconds - departure_seconds) / (arrival_seconds - departure_seconds)
    fraction = max(0.0, min(1.0, fraction))
    return (
        start[0] + fraction * (end[0] - start[0]),
        start[1] + fraction * (end[1] - start[1]),
    )


def time_to_seconds(value: str) -> int:
    """Convert GTFS HH:MM:SS to seconds after service-day midnight."""
    hours, minutes, seconds = map(int, value.split(":"))
    return hours * 3600 + minutes * 60 + seconds



def get_train_segment(
    stops: list[dict],
    current_time: str,
) -> dict | None:
    """Find a train's position between consecutive stations."""

    now = time_to_seconds(current_time)

    if not stops:
        return None

    first_departure = time_to_seconds(stops[0]["departure"])
    last_arrival = time_to_seconds(stops[-1]["arrival"])

    if now < first_departure or now > last_arrival:
        return None

    for index in range(len(stops) - 1):
        current_stop = stops[index]
        next_stop = stops[index + 1]

        arrival = time_to_seconds(current_stop["arrival"])
        departure = time_to_seconds(current_stop["departure"])
        next_arrival = time_to_seconds(next_stop["arrival"])

        # Train is waiting at a station.
        if arrival <= now < departure:
            return {
                "status": "stopped",
                "station": current_stop["station"],
                "stop_id": current_stop["stop_id"],
                "arrival": current_stop["arrival"],
                "departure": current_stop["departure"],
                "progress": 0.0,
            }

        # Train is travelling to the next station.
        if departure <= now < next_arrival:
            duration = next_arrival - departure

            if duration <= 0:
                continue

            progress = (now - departure) / duration

            return {
                "status": "moving",
                "from": current_stop["station"],
                "to": next_stop["station"],
                "from_stop_id": current_stop["stop_id"],
                "to_stop_id": next_stop["stop_id"],
                "departure": current_stop["departure"],
                "arrival": next_stop["arrival"],
                "progress": progress,
            }

    # Train has reached its final station.
    if now == last_arrival:
        last_stop = stops[-1]

        return {
            "status": "stopped",
            "station": last_stop["station"],
            "stop_id": last_stop["stop_id"],
            "arrival": last_stop["arrival"],
            "departure": last_stop["departure"],
            "progress": 1.0,
        }

    return None
