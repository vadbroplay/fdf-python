<h1>
  FdF — карта высот
  <a href="https://github.com/vadbroplay/fdf-python/actions/workflows/checks.yml">
    <img src="https://github.com/vadbroplay/fdf-python/actions/workflows/checks.yml/badge.svg?branch=additional-ci" alt="Python CI">
  </a>
</h1>

<p align="center">
  <img src="docs/screenshot1.png" width="700" alt="Приложение FdF">
</p>

Учебный проект на Python для визуализации трёхмерной карты высот в изометрической проекции.

## Возможности

- Загрузка карты высот из файла `.fdf`.
- Проверка формата входных данных.
- Построение карты в виде точек и соединяющих их рёбер.
- Автоматическое размещение карты по центру окна.
- Обновление отображения при изменении размера окна.

## Требования

- Python 3.12 или новее.
- Tkinter.

## Запуск

Клонируйте репозиторий и перейдите в каталог проекта:

```bash
git clone https://github.com/vadbroplay/fdf-python.git
cd fdf-python
```

Создайте виртуальное окружение и установите зависимости для разработки:

```bash
python -m venv .venv
```

В Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Установите проект и инструменты разработки:

```bash
python -m pip install -e ".[dev]"
```

Запустите программу, указав путь к файлу карты:

```bash
python main.py maps/elem.fdf
```

## Управление

- `Esc` — закрыть приложение.

## Проверки

Запуск тестов:

```bash
python -m pytest
```

Проверка стиля кода:

```bash
python -m ruff check .
```

Проверка типов:

```bash
python -m mypy --strict fdf main.py
```
