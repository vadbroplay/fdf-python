from pathlib import Path

import pytest

from fdf.errors import MapFormatError
from fdf.model import Map, Point
from fdf.parser import parse_map


def write_map(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "test.fdf"
    path.write_text(text, encoding="utf-8")
    return path



def test_parse_elem_map() -> None:
    path = Path("maps/elem.fdf")
    height_map = parse_map(path)

    assert height_map.width == 5
    assert height_map.height == 5
    assert len(height_map) == 25

    center = height_map.rows[2][2]
    assert center.z == 5
    assert (center.x, center.y) == (2, 2)

    assert (height_map.rows[0][0].x, height_map.rows[0][0].y) == (0, 0)
    assert (height_map.rows[4][4].x, height_map.rows[4][4].y) == (4, 4)




@pytest.mark.parametrize(
    "filename",
    [
        "empty.fdf",
        "ragged.fdf",
        "non_integer.fdf",
        "bad_color.fdf",
        "long_color.fdf",
        "bad_separator.fdf",
        "empty_row.fdf",
    ],
)
def test_invalid_maps_raise_error(filename: str) -> None:
    path = Path("maps") / "bad" / filename

    with pytest.raises(MapFormatError):
        parse_map(path)



@pytest.mark.parametrize(
    ("value", "expected_z", "expected_color"),
    [
        ("7", 7, None),
        ("-3", -3, None),
        ("2,0xFF8800", 2, "#FF8800"),
        ("1,0xff", 1, "#0000FF"),
    ],
)
def test_parse_values(
    tmp_path: Path,
    value: str,
    expected_z: int,
    expected_color: str | None,
) -> None:
    path = write_map(tmp_path, value)
    height_map = parse_map(path)
    point = height_map.rows[0][0]

    assert point.z == expected_z
    assert point.color == expected_color



def test_trailing_blank_lines_are_ignored(tmp_path: Path) -> None:
    path = write_map(tmp_path, "1 2\n3 4\n\n")
    height_map = parse_map(path)

    assert height_map.width == 2
    assert height_map.height == 2


def test_missing_file_raises_os_error(tmp_path: Path) -> None:
    path = tmp_path / "missing.fdf"

    with pytest.raises(OSError):
        parse_map(path)


def test_neighbors_of_corner_point() -> None:
    height_map = Map(
        [
            [Point(0, 0, 0), Point(1, 0, 0)],
            [Point(0, 1, 0), Point(1, 1, 0)],
        ]
    )

    neighbors = height_map.neighbors(height_map.rows[0][0])

    assert len(neighbors) == 2
    assert {point.x for point in neighbors} == {0, 1}
