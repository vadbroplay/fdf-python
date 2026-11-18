import sys

from fdf.app import FdfApp
from fdf.errors import FdfError
from fdf.parser import parse_map


def main() -> int:
    """Загружает карту и запускает графическое приложение."""
    if len(sys.argv) != 2:
        print(
            "Использование: python main.py <файл.fdf>",
            file=sys.stderr,
        )
        return 2

    try:
        height_map = parse_map(sys.argv[1])
    except (FdfError, OSError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1

    app = FdfApp(height_map)
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
