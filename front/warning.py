from tkinter import messagebox

def show_warning():
    
    warning_text = """Перед началом работы с приложением, убедитесь, что вы:

•   настроили группу wireshark, позволяющую использовать Dumpcap/Tshark без root прав;

•   являетесь участником группы wireshark;

•   захватываете RTSP-поток при помощи VLC, ffmpeg или другого ПО;

•   не захватываете один и тот же RTSP-поток несколько раз (прим. одновременно открыты VLC и веб-интерфейс). 
"""

    messagebox.showwarning("ВАЖНО", warning_text)