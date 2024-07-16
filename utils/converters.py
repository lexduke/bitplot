from time import strftime, localtime
from front.warnings import show_warning
from subprocess import Popen, PIPE


def epoch_to_datetime(epoch: int) -> str:
    """
    Перевод Unix-времени (epoch) в формат ГГГГ-ММ-ДД чч:мм:cc.
    """
    return strftime("%Y-%m-%d %H:%M:%S", localtime(epoch))


def seconds_to_hms(seconds: int) -> str:
    """
    Перевод секунд в строковое отображение чч:мм:cc.
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d} ч. {minutes:02d} мин. {seconds:02d} сек."


def pcapng_to_csv(path_to_pcapng: str, path_to_csv: str) -> None:
    """
    Конверсия .pcapng файла в .csv при помощи tshark (wireshark) с
    отсечением излишней информации для экономии места на диске и
    ускорения обработки данных. В .csv переносятся следующие данные:
        frame.time_epoch: Время захвата фрейма (в Unix-времени - epoch)
        ip.addr: IP адрес отправителя фрейма
        frame.len: Величина фрейма (в битах)
    Файл .csv сохраняется без хедера. Порядок записи данных в строке:
        frame.time_epoch,ip.addr,frame.len

    Args:
        path_to_pcapng (str): Путь до файла .pcapng
        path_to_csv (str): Путь сохранения файла .csv
    """

    # Субпроцесс конверсии
    cmd = ( "tshark"
            "-T fields "
            "-e frame.time_epoch "
            "-e ip.addr "
            "-e frame.len "
            "-E separator=, "
            f"-r {path_to_pcapng} > {path_to_csv}"
        )
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)

    # При ошибке вывести сообщение на фронт
    stderr = proc.communicate()[1]
    return_code = proc.returncode
    if not return_code == 0:
        show_warning(stderr.decode())
