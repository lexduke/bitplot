import os
import data.front as front
import data.config as config
import data.bpt_parser as bpt_parser



reciever_ip = str()
senders_ips = list()
parsing_time = int()
analyse_time = int()
root_path = os.path.dirname(os.path.abspath(__file__))
pcapng_path = str()
csv_path = str()
config_path = root_path+'/settings.ini'



def set_reciever_ip():
    global reciever_ip

    front.erase_line()
    ip_is_valid = True
    
    ip = input('Введите IP для назначения (макс. 255.255.255.255): ')
    ip_numbers = ip.split(".")
    
    if len(ip_numbers) != 4:
        ip_is_valid = False

    for number in ip_numbers:
        try:
            number = int(number)
            if not number in range(0, 256): ip_is_valid = False
        except ValueError:
            ip_is_valid = False
    
    if ip_is_valid:
        reciever_ip = ip


def add_sender_ip():
    front.erase_line()
    ip_is_valid = True
    
    ip = input('Введите IP для добавления (макс. 255.255.255.255): ')
    ip_numbers = ip.split(".")
    
    if len(ip_numbers) != 4:
        ip_is_valid = False

    for number in ip_numbers:
        try:
            number = int(number)
            if not number in range(0, 256): ip_is_valid = False
        except ValueError:
            ip_is_valid = False
    
    if ip_is_valid:
        senders_ips.append(ip)


def delete_sender_ip():
    while True:
        if len(senders_ips) == 0:
            break

        front.clear()
        front.show_logo()
        front.show_delete_menu(senders_ips)

        choice = input('Выберите IP для удаления: ')

        try:
            choice = int(choice)
        except ValueError:
            break

        if choice in range(1, len(senders_ips)+1) and senders_ips[choice-1]:
            del senders_ips[choice-1]
        else:
            break



def update_analyse_time():
    global analyse_time
    analyse_time = parsing_time



def set_parsing_time():
    global parsing_time

    front.erase_line()
    
    time = input('Введите время сбора данных в секундах (макс. 999999): ')
    
    try:
        time = int(time)
        if time in range(1, 1000000):
            parsing_time = time
            update_analyse_time()
    except ValueError:
        pass



def load_config(path):
    global reciever_ip, senders_ips, parsing_time, pcapng_path, csv_path
    from configparser import NoSectionError
    front.erase_line()
    
    try:
        config_data = config.get_config(path)
    except NoSectionError:
        config_data = None
    
    if not config_data:
        input("Данные конфигурации повреждены или отсутствуют!\nНажмите Enter, чтобы продолжить...")
        config.make_config(path)
    # else:
    reciever_ip, senders_ips, parsing_time, path_to_pcapng, path_to_csv = config.get_config(path)
    if path_to_pcapng:
        pcapng_path = path_to_pcapng
    if path_to_csv:
        csv_path = path_to_csv
    update_analyse_time()



def save_config(path, reciever_ip, senders_ips, parsing_time, pcapng_path, csv_path):
    front.erase_line()
    save_confirm = input('Это действие перезапишет старые данные. Вы уверены? [y/n]:')
    match save_confirm:
        case "y":
            config.set_config(path, reciever_ip, senders_ips, parsing_time, pcapng_path, csv_path)
        case _:
            pass




def parse_data(skip_sniffing = False, skip_converting = False):
    global senders_ips, parsing_time, pcapng_path, csv_path
    
    from time import time

    front.clear()

    sudo_pswd = bpt_parser.get_sudo()

    start_time = time() # Отсчет общего времени для выполнения всех задач

    if not skip_sniffing:

        bpt_parser.sniff_data(parsing_time, pcapng_path, sudo_pswd)
    if not skip_converting:
        if os.path.isfile(pcapng_path) == False:
            del sudo_pswd
            return input('Файл bpt.pcapng не найден! Нажмите Enter, чтобы продолжить...')
        bpt_parser.convert_to_csv(pcapng_path, csv_path, sudo_pswd)
    
    if os.path.isfile(csv_path) == False:
        del sudo_pswd
        return input('Файл bpt.csv не найден! Нажмите Enter, чтобы продолжить...')
    
    del sudo_pswd

    try:
        epoch_start, epoch_end = bpt_parser.get_epoch(csv_path)
    except StopIteration:
        return input('''Данные не найдены! Нажмите Enter для продолжения...

!!! Для предотвращения повтора ошибки проверьте !!!
    
    <> При записи новых данных:    
        - Указан ли в настройках IP камеры (минимум одной);
        - Принимается ли RTSP поток с требуемой камеры; 
        - Соответствует ли IP камеры, указанный в настройках, IP-адресам записанных устройств.
    
    <> При анализе старых данных:
        - Записана ли какая-либо информация в анализируемых файлах.''')
    
    try:
        os.mkdir('./plots')
    except FileExistsError:
        pass

    bpt_parser.create_all_plots(senders_ips, csv_path, epoch_start, epoch_end)

    end_time = time() # Конец отсчета времени | Имеет смысл только при сохранении изображений, а не их отображении

    print(f"Общее время работы: {end_time - start_time} сек")



def main_menu():
    while True:
        front.clear()
        front.show_logo()
        front.show_main_menu(reciever_ip, senders_ips, parsing_time, analyse_time)


        choice = input('Выберите пункт: ')

        match choice: 
            case '1': set_reciever_ip()
            case '2': add_sender_ip()
            case '3':
                if len(senders_ips) > 0: delete_sender_ip()
                else: pass
            case '4': set_parsing_time()
            case '5': load_config(config_path)
            case '6': save_config(config_path, reciever_ip, senders_ips, parsing_time, pcapng_path, csv_path)
            case '7': parse_data()
            case '8': parse_data(True)
            case '9': parse_data(True, True)
            case '0': front.clear(); quit()
            case _: pass




if __name__ == "__main__":
    front.clear()
    load_config(config_path)
    main_menu()