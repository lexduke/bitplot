import configparser

def make_config(path):
    with open(path, 'w') as file:
        file.write('''[Main]
resiever_ip =
senders_ips =
parsing_time =

[Files]
path_to_pcapng = /tmp/bpt.pcapng
path_to_csv = /tmp/bpt.csv
''')




def set_config(path, reciever_ip, senders_ips, parsing_time, path_to_pcapng, path_to_csv):

    conf = configparser.ConfigParser()
    conf.add_section('Main')
    conf.set('Main', 'resiever_ip', str(reciever_ip))
    conf.set('Main', 'senders_ips', ','.join(senders_ips))
    conf.set('Main', 'parsing_time', str(parsing_time))
    conf.add_section('Files')
    conf.set('Files', 'path_to_pcapng', str(path_to_pcapng))
    conf.set('Files', 'path_to_csv', str(path_to_csv))
    
    with open(path, "w") as config_file:
        conf.write(config_file)
 

def get_config(path):
    conf = configparser.ConfigParser()
    conf.read(path)

    try:
        reciever_ip    =  conf.get('Main',  'resiever_ip')
        senders_ips    =  conf.get('Main',  'senders_ips')
        parsing_time   =  conf.get('Main',  'parsing_time')
        path_to_pcapng =  conf.get('Files', 'path_to_pcapng')
        path_to_csv    =  conf.get('Files', 'path_to_csv')

        if not reciever_ip or reciever_ip == "None":
            reciever_ip = str()
        if not senders_ips or senders_ips == "None":
            senders_ips = list()
        else:
            senders_ips = senders_ips.split(',')
        if not parsing_time or parsing_time == "None":
            parsing_time = int()
        else:
            parsing_time =  int(parsing_time)
        if not path_to_pcapng or path_to_pcapng == "None":
            path_to_pcapng = '/tmp/bpt.pcapng'
        if not path_to_csv or path_to_csv == "None":
            path_to_csv = '/tmp/bpt.csv'


        return reciever_ip, senders_ips, parsing_time, path_to_pcapng, path_to_csv
    
    except ValueError or TypeError:
        return False

if __name__ == '__main__':
    exit()