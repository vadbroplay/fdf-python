from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:

    x: int
    y: int
    z: int
    color: str | None = None


class Map:

    def __init__(self, rows: list[list[Point]]) -> None:
        if not rows or not rows[0]:
            raise ValueError("Карта не может быть пустой")

        width = len(rows[0])
        if any(len(row) != width for row in rows):
            raise ValueError("Все строки карты должны иметь одинаковую длину")

        self.rows = rows
        self.width = width
        self.height = len(rows)

    def __len__(self) -> int:
        return self.width * self.height

    def __iter__(self) -> Iterator[Point]:
        for row in self.rows:
            yield from row

    def neighbors(self, point: Point) -> list[Point]:
        result: list[Point] = []
        x, y = point.x, point.y

        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy

            if 0 <= nx < self.width and 0 <= ny < self.height:
                result.append(self.rows[ny][nx])

        return result
