from os import SEEK_END, SEEK_CUR
from time import time, strftime, localtime
from math import ceil
from subprocess import Popen, PIPE
from getpass import getpass
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MultipleLocator
from matplotlib.style import use as use_style
from datetime import datetime



### ### Декораторы ### ###

def timer(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time()
            print(f'Выполнение "{name}": Начато')
            result = func(*args, **kwargs)
            end_time = time()
            execution_time = end_time - start_time
            print(f'Выполнение "{name}": Завершено - {execution_time} сек')
            return result
        return wrapper
    return decorator


### ### Lambda ### ###

epoch_to_datetime = lambda epoch_time: strftime('%Y-%m-%d %H:%M:%S', localtime(epoch_time))
 


### ### Методы ### ###

### Проверка пароля администратора

def check_password(password): # Проверка и передача пароля администратора другим подпроцессам. Не знаю, как сделать это безопаснее
    
    cmd = 'sudo -S echo "Password is valid"'

    proc = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    proc.communicate(password.encode())

    return_code = proc.returncode
    if return_code == 0:
        return True
    else:
        print('Ошибка: Неверный пароль!')
        return False


def get_sudo():

    while True:
        pswd = getpass('Введите пароль [sudo]:')
        
        if check_password(pswd):
            return pswd


### Сторонние процессы сбора информации

@timer('Сбор данных')
def sniff_data(duration, path, password):

    current_time = time()
    print(f'Начало записи: {epoch_to_datetime(current_time)}, завершение: {epoch_to_datetime(current_time+duration)}')

    cmd = f'sudo -S dumpcap -a duration:{str(duration)} -i any -f udp -s 32 -w {path}'

    proc = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    err = proc.communicate(password.encode())[1]

    return_code = proc.returncode

    if return_code == 0:
        return True
    else:
        print('Ошибка:', err.decode())
        return False


@timer('Обработка данных')
def convert_to_csv(path_from, path_to, password):

    cmd = f'sudo -S tshark -T fields -e frame.time_epoch -e ip.addr -e frame.len -E separator=, -r {path_from} > {path_to}'

    proc = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    err = proc.communicate(password.encode())[1]

    return_code = proc.returncode

    if return_code == 0:
        return True
    else:
        print('Ошибка:', err.decode())
        return False


# Получение времени epoch

@timer('Обработка времени')
def get_epoch(path): # Получение epoch из первой и последней строки csv при помощи seek, SEEK_END и SEEK_CUR
                     # Это намного эффективнее и быстрее, чем перебирать циклом for

    file = open(path, 'rb') # Обязательно бинарное чтение, иначе не будет работать
        
    try:
        first_line = next(file).decode()
    except StopIteration as exception:
        raise exception


    try:  # Словить ошибку на случай однострочного файла (что маловероятно)
        file.seek(-2, SEEK_END)
        while file.read(1) != b'\n':
            file.seek(-2, SEEK_CUR)
    except OSError:
        file.seek(0)

    last_line = file.readline().decode()

    file.close()

    epoch_start = ceil(float(first_line.split(',')[0]))
    epoch_end   = ceil(float(last_line.split(',')[0]))

    return epoch_start, epoch_end



@timer('Обработка битрейта')
def get_bitrate(path, ip, epoch_list):  # Выполнен перебором for - самый оптимальный по скорость/ОЗУ. Есть альтернативный, почти мгновенный вариант с
                                        # использованнием numpy, но он выгружает весь файл в ОЗУ, что самоубийственно с предполагаемыми объемами данных.
  
    print('Обработка битрейта камеры', ip)
    
    bitrate_dict = dict.fromkeys(epoch_list, 0)

    file = open(path, 'r')

    for line in file:
        line_list = line.split(',')

        if str(line_list[1]) == ip:
            bitrate_dict[ceil(float(line_list[0]))] += int(line_list[2])*8  # Отказ от доп. переменных ухудшил читаемость, но ускорил перебор в 2 раза
    
    file.close()

    return list(bitrate_dict.values())




def create_plot(ips, path_to_csv, epoch_start, epoch_end, ylim = None, enum = 1):

    date_duration = f'{epoch_to_datetime(epoch_start).replace(" ","_")}_{epoch_to_datetime(epoch_end).replace(" ","_")}'
    time_delta = epoch_end - epoch_start

    date_list = [datetime.fromtimestamp(i) for i in range(epoch_start, epoch_end+1, 1)]

    use_style('seaborn-v0_8')
    fig, ax = plt.subplots(layout="constrained")
    
    for ip in ips:
        if len(ips) > 1:
            ax.plot(date_list, get_bitrate(path_to_csv, ip, range(epoch_start, epoch_end+1, 1)), label=ip, alpha=0.8)
        else:
            ax.plot(date_list, get_bitrate(path_to_csv, ip, range(epoch_start, epoch_end+1, 1)), label=ip, color='C'+str(enum))
    ax.set_ylabel('Битрейт')
    if ylim:
        ax.set_ylim(*ylim)
    else:
        ax.set_ylim(0)
    ylim = ax.get_ylim()
    ax.yaxis.set_major_locator(MultipleLocator(5*10**5))

    ax.set_xlabel('Дата')
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S\n%d-%m-%Y'))
    
    ax.set_title('График битрейта')
    ax.legend()
    fig.set_size_inches(19.2, 10.8)
    
    if len(ips) > 1:
        image_name = f'./plots/recording_{date_duration}/multiple/multiple_{date_duration}.png'
    else:
        str_ip = str(*ips)
        image_name = f'./plots/recording_{date_duration}/{str_ip}/{str_ip}_{date_duration}.png'

    plt.savefig(image_name, bbox_inches='tight', dpi=200)
    
    if time_delta <= 2000: # Прекратить выполнение при длительности записи менее 2000 сек
        return ylim

    epoch_start_limit = (epoch_start // 1800) * 1800
    epoch_end_limit   = (epoch_end // 1800 + 1) * 1800

    limits_list = [[i, i+1800] for i in range(epoch_start_limit, epoch_end_limit, 1800)]
    
    for segment in limits_list:
        segment_duration = f'{epoch_to_datetime(segment[0]).replace(" ","_")}_{epoch_to_datetime(segment[1]).replace(" ","_")}'
        if len(ips) > 1:
            image_name = f'./plots/recording_{date_duration}/multiple/multiple_{segment_duration}.png'
        else:
            str_ip = str(*ips)
            image_name = f'./plots/recording_{date_duration}/{str_ip}/{str_ip}_{segment_duration}.png'
        
        ax.set_xlim(left=datetime.fromtimestamp(segment[0]), right=datetime.fromtimestamp(segment[1]))
        plt.savefig(image_name, bbox_inches='tight', dpi=200)


    return ylim




def create_all_plots(ip_list, path_to_csv, epoch_start, epoch_end):
    from os import mkdir

    date_duration = f'{epoch_to_datetime(epoch_start).replace(" ","_")}_{epoch_to_datetime(epoch_end).replace(" ","_")}'
    try:
        mkdir(f'./plots/recording_{date_duration}')
    except FileExistsError:
        pass

    if len(ip_list) > 1:
        try:
            mkdir(f'./plots/recording_{date_duration}/multiple')
        except FileExistsError:
            pass


    for ip in ip_list:
        try:
            mkdir(f'./plots/recording_{date_duration}/{ip}')
        except FileExistsError:
            pass    
    
    ylim = create_plot(ip_list, path_to_csv, epoch_start, epoch_end)
    if len(ip_list) > 1:
        for ip in ip_list:
            create_plot([ip], path_to_csv, epoch_start, epoch_end, ylim, ip_list.index(ip))


if __name__ == '__main__':
    exit()
