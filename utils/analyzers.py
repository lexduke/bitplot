from math import ceil
from os import SEEK_CUR, SEEK_END


def get_epoch(path_to_csv: str) -> tuple[int, int]:
    """
    Получение Unix-времени (epoch) из первой и последней строки .csv при
    помощи seek, SEEK_END и SEEK_CUR. Это намного эффективнее и быстрее,
    чем перебирать циклом for.

    Args:
        path_to_csv (str): Путь до .csv файла

    Raises:
        exception: Отлов ошибки на случай однострочного файла (маловероятно)

    Returns:
        tuple[int, int]: Время начала и конца записи в Unix-времени (epoch)
    """

    file = open(path_to_csv, "rb")  

    try:
        first_line = next(file).decode()
    except StopIteration as exception:
        raise exception

    try:
        file.seek(-2, SEEK_END)
        while file.read(1) != b"\n":
            file.seek(-2, SEEK_CUR)
    except OSError:
        file.seek(0)

    last_line: str = file.readline().decode()

    file.close()

    epoch_start: int = ceil(float(first_line.split(",")[0]))
    epoch_end: int = ceil(float(last_line.split(",")[0]))

    return epoch_start, epoch_end


def get_bitrate(path_to_csv: str, ip: str, epoch_list: list[int]) -> list[int]:
    """
    Парсинг битрейта по конкретному IP адресу в .csv файле. 

    Выполнен перебором for - самый оптимальный по скорость/ОЗУ. Есть
    альтернативный, почти мгновенный вариант с использованнием numpy, но
    он выгружает весь файл в ОЗУ, что самоубийственно с предполагаемыми
    объемами данных.

    Args:
        path_to_csv (str): Путь до .csv файла.
        ip (str): Искомый IP адрес.
        epoch_list (list[int]): Промежуток времени в виде списка из
                                секунд Unix-времени (epoch) 

    Returns:
        list[int]: Список значений битрейта по указанному IP адресу за
                   указанный промежуток времени.
    """

    bitrate_dict = dict.fromkeys(epoch_list, 0)

    file = open(path_to_csv, "r")

    for line in file:
        line_list = line.split(",")

        if str(line_list[1]) == ip:
            bitrate_dict[ceil(float(line_list[0]))] += int(line_list[2]) * 8

    file.close()

    return list(bitrate_dict.values())


def get_min_avg_max(ip_list, path_to_csv, epoch_start, epoch_end) -> dict:
    min_avr_max_dict = dict()

    for ip in ip_list:
        values_list: list[int] = get_bitrate(
            path_to_csv, ip, range(epoch_start, epoch_end + 1, 1)
        )

        if len(values_list) < 3:
            min_avr_max_dict[ip] = None

        else:
            # Избавляемся от первого и последнего значения, т.к. они могут быть нулями
            values_list.pop(0)
            values_list.pop(-1)

            # Получаем значения
            minimum: int = min(values_list)
            average: int = ceil(sum(values_list) / len(values_list))
            maximum: int = max(values_list)

            min_avr_max_dict[ip] = [minimum, average, maximum]

    return min_avr_max_dict
