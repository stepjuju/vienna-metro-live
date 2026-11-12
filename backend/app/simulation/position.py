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
