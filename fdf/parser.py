import re
from pathlib import Path

from fdf.errors import MapFormatError
from fdf.model import Map, Point

_COLOR_PATTERN = re.compile(r"0x[0-9a-fA-F]{1,6}\Z")


def parse_map(path: str | Path) -> Map:
    """Читает файл FdF и возвращает карту высот.

    Ошибки формата вызывают MapFormatError.
    Ошибки доступа к файлу передаются вызывающему коду.
    """
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        raise MapFormatError("Файл карты пуст")

    rows: list[list[Point]] = []
    expected_width: int | None = None

    for y, line in enumerate(lines, start=1):
        tokens = line.split()

        if not tokens:
            raise MapFormatError(
                f"строка {y}, колонка 1: пустая строка внутри карты"
            )

        if expected_width is None:
            expected_width = len(tokens)
        elif len(tokens) != expected_width:
            raise MapFormatError(
                f"строка {y}: ожидалось {expected_width} значений, "
                f"получено {len(tokens)}"
            )

        row: list[Point] = []

        for x, token in enumerate(tokens):
            parts = token.split(",")

            if len(parts) > 2:
                raise MapFormatError(
                    f"строка {y}, колонка {x + 1}: "
                    f"{token!r} — неверный формат значения"
                )

            height_text = parts[0]

            try:
                z = int(height_text)
            except ValueError as exc:
                raise MapFormatError(
                    f"строка {y}, колонка {x + 1}: "
                    f"{height_text!r} — не целое число"
                ) from exc

            color: str | None = None

            if len(parts) == 2:
                raw_color = parts[1]

                if not _COLOR_PATTERN.fullmatch(raw_color):
                    raise MapFormatError(
                        f"строка {y}, колонка {x + 1}: "
                        f"{raw_color!r} — некорректный цвет"
                    )

                color_value = int(raw_color, 0)
                color = f"#{color_value:06X}"

            row.append(Point(x=x, y=y - 1, z=z, color=color))

        rows.append(row)

    return Map(rows)
