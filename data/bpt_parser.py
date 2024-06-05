from os import SEEK_END, SEEK_CUR, mkdir
from math import ceil
from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MultipleLocator, FuncFormatter
from matplotlib.style import use as use_style
from datetime import datetime

from front.warnings import show_warning
from utils.converters import epoch_to_datetime


### ### Методы ### ###

### Сторонние процессы сбора информации
def sniff_data(duration, path):
    
    # path = path+'/bpt.pcapng'
    
    cmd = ['dumpcap', '-a', f'duration:{str(duration)}', '-i', 'any', '-f', 'udp', '-s', '32', '-w', path]
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stderr = proc.communicate()[1]
    return_code = proc.returncode
    if not return_code == 0:
        show_warning(stderr.decode())


def get_epoch(path):
    '''
    Получение epoch из первой и последней строки csv при помощи seek, SEEK_END и SEEK_CUR
    Это намного эффективнее и быстрее, чем перебирать циклом for
    '''

    # path = path+'/bpt.csv'

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


def get_bitrate(path, ip, epoch_list):
    '''
    Выполнен перебором for - самый оптимальный по скорость/ОЗУ. Есть альтернативный, почти мгновенный вариант с
    использованнием numpy, но он выгружает весь файл в ОЗУ, что самоубийственно с предполагаемыми объемами данных.
    '''
    
    bitrate_dict = dict.fromkeys(epoch_list, 0)

    file = open(path, 'r')

    for line in file:
        line_list = line.split(',')

        if str(line_list[1]) == ip:
            bitrate_dict[ceil(float(line_list[0]))] += int(line_list[2])*8
    
    file.close()

    return list(bitrate_dict.values())


def get_min_avg_max(ip_list, path_to_csv, epoch_start, epoch_end) -> dict:
    min_avr_max_dict = dict()

    for ip in ip_list:
        values_list = get_bitrate(path_to_csv, ip, range(epoch_start, epoch_end+1, 1))
    
        if len(values_list) < 3:
            min_avr_max_dict[ip] = None

        else:
            # Избавляемся от первого и последнего значения, т.к. они могут быть нулями
            values_list.pop(0)
            values_list.pop(-1)

            # Получаем значения
            minimum = min(values_list)
            average = ceil(sum(values_list) / len(values_list))
            maximum = max(values_list)

            min_avr_max_dict[ip] = [minimum, average, maximum]

    return min_avr_max_dict


def create_plot(ip_list, path_to_csv, epoch_start, epoch_end, ylim = None, enum = 1):

    date_duration = f'{epoch_to_datetime(epoch_start).replace(" ","_")}_{epoch_to_datetime(epoch_end).replace(" ","_")}'
    time_delta = epoch_end - epoch_start

    date_list = [datetime.fromtimestamp(i) for i in range(epoch_start, epoch_end+1, 1)]

    use_style('seaborn-v0_8')

    fig, ax = plt.subplots(layout="constrained")
    
    for ip in ip_list:
        if len(ip_list) > 1:
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

    def millions_formatter(y, pos):
        return '%1dkbps' % (y * 1e-3)

    ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

    ax.set_xlabel('Дата')
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S\n%d-%m-%Y'))
    
    ax.set_title('График битрейта')
    ax.legend()
    fig.set_size_inches(19.2, 10.8)
    
    if len(ip_list) > 1:
        image_name = f'./plots/recording_{date_duration}/multiple/multiple_{date_duration}.png'
    else:
        str_ip = str(*ip_list)
        image_name = f'./plots/recording_{date_duration}/{str_ip}/{str_ip}_{date_duration}.png'

    plt.savefig(image_name, bbox_inches='tight', dpi=200)
    
    if time_delta <= 2000: # Прекратить выполнение при длительности записи менее 2000 сек
        plt.close(fig)
        return ylim

    epoch_start_limit = (epoch_start // 1800) * 1800
    epoch_end_limit   = (epoch_end // 1800 + 1) * 1800

    limits_list = [[i, i+1800] for i in range(epoch_start_limit, epoch_end_limit, 1800)]
    
    for segment in limits_list:
        segment_duration = f'{epoch_to_datetime(segment[0]).replace(" ","_")}_{epoch_to_datetime(segment[1]).replace(" ","_")}'
        if len(ip_list) > 1:
            image_name = f'./plots/recording_{date_duration}/multiple/multiple_{segment_duration}.png'
        else:
            str_ip = str(*ip_list)
            image_name = f'./plots/recording_{date_duration}/{str_ip}/{str_ip}_{segment_duration}.png'
        
        ax.set_xlim(left=datetime.fromtimestamp(segment[0]), right=datetime.fromtimestamp(segment[1]))
        plt.savefig(image_name, bbox_inches='tight', dpi=200)
        plt.close(fig)
        
    return ylim


def create_directory(path):
    try:
        mkdir(path)
    except FileExistsError:
        pass


def create_files(ip_list: list, path_to_csv: str, epoch_start: int, epoch_end: int) -> None:
    # pass

    date_duration = f'{epoch_to_datetime(epoch_start).replace(" ","_")}_{epoch_to_datetime(epoch_end).replace(" ","_")}'

    create_directory(f'./plots/recording_{date_duration}')

    if len(ip_list) > 1:
        create_directory(f'./plots/recording_{date_duration}/multiple')

    for ip in ip_list:
        create_directory(f'./plots/recording_{date_duration}/{ip}')

    
    min_avg_max_values = get_min_avg_max(ip_list, path_to_csv, epoch_start, epoch_end)

    for ip in ip_list:
        
        if min_avg_max_values[ip]:

            minimum, average, maximum = min_avg_max_values[ip]
            
            with open(f'./plots/recording_{date_duration}/{ip}/bitrate_info.txt', 'a', encoding='utf-8') as file:
                lines = [
                    'Минимальный битрейт: '+str(minimum/1000)+' kbps\n',
                    'Средний битрейт: '+str(average/1000)+' kbps\n',
                    'Максимальный битрейт: '+str(maximum/1000)+' kbps\n'
                ]

                file.writelines(lines)


    ylim = create_plot(ip_list, path_to_csv, epoch_start, epoch_end)

    if len(ip_list) > 1:
        for ip in ip_list:
            create_plot([ip], path_to_csv, epoch_start, epoch_end, ylim, ip_list.index(ip))
    



if __name__ == '__main__':
    pass
