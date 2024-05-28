from time import strftime, localtime
from front.warnings import show_warning
from subprocess import Popen, PIPE

epoch_to_datetime = lambda epoch_time: strftime('%Y-%m-%d %H:%M:%S', localtime(epoch_time))

def seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d} ч. {minutes:02d} мин. {seconds:02d} сек."

def pcapng_to_csv(path_from, path_to):

    # path_from = path_from+'/bpt.pcapng'
    # path_to = path_to+'/bpt.csv'

    cmd = f'tshark -T fields -e frame.time_epoch -e ip.addr -e frame.len -E separator=, -r {path_from} > {path_to}'
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stderr = proc.communicate()[1]
    return_code = proc.returncode
    if not return_code == 0:
        show_warning(stderr.decode())