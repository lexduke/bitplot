from subprocess import Popen, PIPE

from front.warnings import show_warning


def sniff_data(duration: int, path: str) -> None:
    """
    Сбор информации с прослушиваемого RTSP-потока при помощи
    dumpcap (wireshark). Сохраняет .pcapng по указанному пути.

    Args:
        duration (int): Время сбора информации в секундах.
        path (str): Путь сохранения файла .pcapng.
    """

    # Субпроцесс сниффинга
    cmd = [
        "dumpcap",
        "-a", f"duration:{str(duration)}",
        "-i", "any",
        "-f", "udp",
        "-s", "32",
        "-w", path,
    ]
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)

    # При ошибке вывести сообщение на фронт
    stderr = proc.communicate()[1]
    return_code = proc.returncode
    if not return_code == 0:
        show_warning(stderr.decode())
