from os import mkdir


def create_directory(path: str) -> None:
    """
    Создание директории с предварительной проверкой её существования.

    Args:
        path (str): Путь создания директории.
    """
    try:
        mkdir(path)
    except FileExistsError:
        pass