
from fdf.model import Map, Point


def test_map_len() -> None:
    height_map = Map(
        [
            [Point(0, 0, 1), Point(1, 0, 2)],
            [Point(0, 1, 3), Point(1, 1, 4)],
        ]
    )

    assert len(height_map) == 4


def test_map_iteration() -> None:
    height_map = Map(
        [
            [Point(0, 0, 1), Point(1, 0, 2)],
            [Point(0, 1, 3), Point(1, 1, 4)],
        ]
    )

    heights = [point.z for point in height_map]

    assert heights == [1, 2, 3, 4]


def test_neighbors_of_corner_point() -> None:
    height_map = Map(
        [
            [Point(0, 0, 1), Point(1, 0, 2)],
            [Point(0, 1, 3), Point(1, 1, 4)],
        ]
    )

    neighbors = height_map.neighbors(height_map.rows[0][0])

    assert len(neighbors) == 2
    assert {point.z for point in neighbors} == {2, 3}
