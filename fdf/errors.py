class FdfError(Exception):
    """Базовая ошибка приложения FdF."""


class MapFormatError(FdfError):
    """Ошибка формата файла карты высот."""
