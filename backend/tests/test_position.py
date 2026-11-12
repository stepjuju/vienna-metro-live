import pytest

from app.simulation.position import interpolate_position


def test_midway():
    assert interpolate_position((0, 0), (120, 60), 0, 120, 60) == (60, 30)


def test_clamps_before_and_after():
    assert interpolate_position((0, 0), (120, 0), 20, 140, 0) == (0, 0)
    assert interpolate_position((0, 0), (120, 0), 20, 140, 200) == (120, 0)


def test_invalid_interval():
    with pytest.raises(ValueError):
        interpolate_position((0, 0), (120, 0), 10, 10, 10)
