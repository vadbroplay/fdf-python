import math

import pytest

from fdf.model import Map, Point
from fdf.projection import Camera, ScreenPoint


def test_project_origin() -> None:
    camera = Camera(scale=1.0, offset_x=0.0, offset_y=0.0)
    result = camera.project(Point(x=0, y=0, z=0))

    assert result == ScreenPoint(x=0.0, y=0.0)


def test_project_horizontal_point() -> None:
    camera = Camera(scale=1.0, offset_x=0.0, offset_y=0.0)
    result = camera.project(Point(x=1, y=0, z=0))

    assert result.x == pytest.approx(math.cos(math.radians(30)))
    assert result.y == pytest.approx(math.sin(math.radians(30)))


def test_project_vertical_height() -> None:
    camera = Camera(
        scale=1.0,
        offset_x=0.0,
        offset_y=0.0,
        z_scale=2.0,
    )
    result = camera.project(Point(x=0, y=0, z=3))

    assert result.x == pytest.approx(0.0)
    assert result.y == pytest.approx(-6.0)


def test_project_applies_scale_and_offset() -> None:
    camera = Camera(
        scale=2.0,
        offset_x=100.0,
        offset_y=50.0,
    )
    result = camera.project(Point(x=0, y=0, z=0))

    assert result == ScreenPoint(x=100.0, y=50.0)


def test_fit_returns_positive_scale() -> None:
    height_map = Map(
        [
            [Point(0, 0, 0), Point(1, 0, 0)],
            [Point(0, 1, 0), Point(1, 1, 2)],
        ]
    )

    camera = Camera.fit(height_map, width=800, height=600)

    assert camera.scale > 0
    assert camera.offset_x > 0
    assert camera.offset_y > 0


def test_fit_keeps_map_inside_window() -> None:
    height_map = Map(
        [
            [Point(0, 0, 0), Point(1, 0, 1), Point(2, 0, 0)],
            [Point(0, 1, 0), Point(1, 1, 3), Point(2, 1, 0)],
            [Point(0, 2, 0), Point(1, 2, 0), Point(2, 2, 0)],
        ]
    )

    width, height = 800, 600
    camera = Camera.fit(height_map, width, height)

    projected = [camera.project(point) for point in height_map]

    assert min(point.x for point in projected) >= 0
    assert max(point.x for point in projected) <= width
    assert min(point.y for point in projected) >= 0
    assert max(point.y for point in projected) <= height
