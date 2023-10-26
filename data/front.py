from os import system
from sys import stdout
import data.sideapps as sideapps
from math import ceil




clear = lambda: system('clear')




def erase_line():
    # Очищаем строку
    stdout.write('\033[K')
    # Перемещаем курсор в начало строки
    stdout.write('\033[F')




def show_invalid_warning():
    erase_line()

    input("Неверное значение! Нажмите Enter, чтобы продолжить...")




# Логотип
def show_logo():
    print('''\
║                                                                               
║            |    _)  |         /\ 
║             _ \  |   _|      /  \                       
║   /\      _.__/__|_\__|_____/    \ 
║__/  \    /          |        |    \       
║      \  /      _ \  |   _ \   _|   \_____ v.1.1
║       \/      .__/ _| \___/ \__|
║              _|                     
╠═════════════════════════════════════════════════╗
║                                                 ║''')




# Отображение основного меню
def show_main_menu(reciever_ip, senders_ips, parsing_time, analyse_time):

    analyse_time = ceil(parsing_time*(0.012+0.00084*len(senders_ips)))
    whole_time = parsing_time+analyse_time
    
    if reciever_ip:
        print(f'║  IP получателя (ПК):        {reciever_ip}'+' '*(20-len(reciever_ip))+'║')
    else:
        print('║  IP получателя (ПК):        Не задано'+' '*11+'║')
    
    print('║','─'*47,'║')
    
    if len(senders_ips) > 0:
        print(f'║  IP отправителей (камер):   {senders_ips[0]}'+' '*(20-len(senders_ips[0]))+'║')
        for i in senders_ips[1:]:
            print('║'+' '*29+i+' '*(20-len(i))+'║')
    else:
        print('║  IP отправителей (камер):   Не задано'+' '*11+'║')

    print('║'+' '*49+'║')
    print('╠'+'═'*49+'╣')
    print('║'+' '*49+'║')

    if parsing_time:
        print(f'║  Время сбора данных:        {parsing_time} сек'+' '*(16-len(str(parsing_time)))+'║')
    else:
        print('║  Время сбора данных:        Не задано'+' '*11+'║')

    print('║','─'*47,'║')

    if analyse_time:
        print(f'║  Время анализа данных:      {ceil(analyse_time)} сек'+' '*(16-len(str(ceil(analyse_time))))+'║')
        print('║','─'*47,'║')
        print(f'║  Время всего процесса:      {ceil(whole_time)} сек'+' '*(16-len(str(ceil(whole_time))))+'║')
    else:
        print('║  Время анализа данных:      Неизвестно'+' '*10+'║')
        print('║','─'*47,'║')
        print('║  Время всего процесса:      Неизвестно'+' '*10+'║')

    print('║'+' '*49+'║')
    print('╠'+'═'*49+'╣')
    print('║'+' '*49+'║')

    if reciever_ip:
        print('╠═ 1) Изменить IP получателя'+' '*22+'║')
    else:
        print('╠═ 1) Задать IP получателя'+' '*24+'║')

    print('║'+' '*49+'║')
    print('╠═ 2) Добавить IP отправителя'+' '*21+'║')
    print('║'+' '*49+'║')
    
    if len(senders_ips) > 0:
        print('╠═ 3) Удалить IP отправителя'+' '*22+'║')
        print('║'+' '*49+'║')

    print('║','─'*47,'║')
    print('║'+' '*49+'║')

    if parsing_time:
        print('╠═ 4) Изменить время сбора данных'+' '*17+'║')
    else:
        print('╠═ 4) Задать время сбора данных'+' '*19+'║')
    
    print('║'+' '*49+'║')
    print('║','─'*47,'║')
    print('║'+' '*49+'║')
    print('╠═ 5) Загрузить конфигурацию'+' '*22+'║')
    print('║'+' '*49+'║')
    print('╠═ 6) Сохранить конфигурацию'+' '*22+'║')
    print('║'+' '*49+'║')
    print('║','─'*47,'║')
    print('║'+' '*49+'║')
    print('╠═ 7) Запустить запись и анализ новых данных'+' '*6+'║')
    print('║'+' '*49+'║')
    print('╠═ 8) Запустить анализ старых pcapng данных'+' '*7+'║')
    print('║'+' '*49+'║')
    print('╠═ 9) Запустить анализ старых csv данных'+' '*10+'║')
    print('║'+' '*49+'║')
    print('╠═ 0) Выйти'+' '*39+'║')
    print('║'+' '*49+'║')
    print('╚'+'═'*49+'╝')



# Отображение меню удаления IP
def show_delete_menu(senders_ips):
    print('║  Выберите IP из списка для удаления:'+' '*12+'║')
    print('║'+' '*49+'║')
    for i in senders_ips:   
        print(f'╠═ {str(senders_ips.index(i)+1)}) {i}'+' '*(44-len(i))+'║')
    print('║'+' '*49+'║')
    print('╠═ 0) Вернуться'+' '*35+'║')
    print('║'+' '*49+'║')
    print('╚'+'═'*49+'╝')



if __name__ == "__main__":
    exit()