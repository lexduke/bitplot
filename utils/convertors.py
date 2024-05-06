from time import strftime, localtime

epoch_to_datetime = lambda epoch_time: strftime('%Y-%m-%d %H:%M:%S', localtime(epoch_time))

def seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d} ч. {minutes:02d} мин. {seconds:02d} сек."