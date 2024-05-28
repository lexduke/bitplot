from tkinter import messagebox

def show_startup_warning():
    
    warning_text = """Перед началом работы с приложением, убедитесь, что вы:

•   настроили группу wireshark, позволяющую использовать Dumpcap/Tshark без root прав;

•   являетесь участником группы wireshark;

•   захватываете RTSP-поток при помощи VLC, ffmpeg или другого ПО;

•   не захватываете один и тот же RTSP-поток несколько раз (прим. одновременно открыты VLC и веб-интерфейс). 
"""

    messagebox.showwarning("Важно", warning_text)


def show_no_data_warning():
    
    warning_text = """Для предотвращения повтора ошибки проверьте:

•   при записи и анализе новых данных:

    ○ принимаются ли RTSP-потоки с указанных IP-адресов;

•   при анализе старых данных:

    ○ записана ли какая-либо информация в анализируемом файле;

    ○ присутствуют ли указанные IP-адреса в анализируемом файле;
"""

    messagebox.showwarning("Данные не найдены", warning_text)


def show_warning(warning_text):
    messagebox.showwarning("Ошибка", warning_text)