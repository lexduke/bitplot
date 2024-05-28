import os
import tkinter as tk
from tkinter import font
import re
from tkinter.ttk import Separator
from _tkinter import TclError
from math import ceil

from utils.converters import seconds_to_hms
from data.bpt_parser import sniff_data, get_epoch, create_all_plots
from utils.converters import pcapng_to_csv
from front.warnings import show_warning, show_no_data_warning
from front.loading_page import LoadingPage

def validate_number(text):
    # Проверка формата IP-адреса
    pattern = r"^^[1-9][0-9]{0,4}$$"
    return True if re.match(pattern, str(text)) or text == "" else False

def validate_path(entry):
    text = entry.get()
    if os.path.exists(text):
        entry.config(fg='black')  # Черный цвет текста, если путь существует
        return True
    else:
        entry.config(fg='red')  # Красный цвет текста, если путь не существует
        return False


class AddIpFrame(tk.Frame):
    def __init__(self, master=None, listbox_frame=None, delete_frame=None, start_frame=None, **kwargs) -> None:
        super().__init__(master, **kwargs)

        # Ссылки на список IP и кнопки удаления
        self.listbox_frame = listbox_frame
        self.delete_frame = delete_frame
        self.start_frame = start_frame # Необходимо назначать после инициализации объекта класса StartAnalyseFrame

        # Инициализация дочерних элементов
        self.label = tk.Label(self, text='Добавить IP адрес камеры:')
        self.entry = tk.Entry(self, validate='key', validatecommand=(self.register(self.validate_ip), '%P'))
        self.button = tk.Button(self, text='Добавить IP адрес', command=self.add_ip())
        self.button.config(state='disabled')

        # Отображение дочерних элементов
        self.entry.grid(row=0, column=0, sticky='ew', padx='4')
        self.button.grid(row=0, column=1)
        self.columnconfigure(0, weight=1) # Растягиваем add_ip_entry по ширине фрейма

        # Привязываем валидацию к каждому нажатию клавиши в поле ввода
        self.entry.bind('<KeyRelease>', self.update_button_state)

    def validate_ip(self, text):
        # Проверка формата IP-адреса
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){0,3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?){0,1}$'
        return True if re.match(pattern, text) or text == "" else False

    def update_button_state(self, event):
        # Паттерн для проверки формата IP-адреса
        ip_pattern = r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

        if re.match(ip_pattern, self.entry.get()):
            self.button.config(state='normal')
        else:
            self.button.config(state='disabled')
    
    def add_ip(self):
        def add():
            item = self.entry.get()
            if item:
                self.listbox_frame.listbox.insert('end', item)
                self.entry.delete(0, 'end')
            # После удаления элементов обновляем состояние кнопок
            if self.delete_frame:
                self.delete_frame.update_buttons_state()
            if self.start_frame:
                self.start_frame.update_buttons_state()
            self.button.config(state='disabled')
        return add


class DeleteIpsFrame(tk.Frame):
    def __init__(self, master=None, listbox_frame=None, start_frame=None, **kwargs) -> None:
        super().__init__(master, **kwargs)

        # Ссылка на список IP
        self.listbox_frame = listbox_frame
        self.start_frame = start_frame # Необходимо назначать после инициализации объекта класса StartAnalyseFrame

        # Инициализация дочерних элементов
        self.delete_selected_button = tk.Button(self, text='Удалить выбранные', command=self.delete_selected_ips())
        self.delete_all_button = tk.Button(self, text='Отчистить список', command=self.delete_all_ips())

        # Отображение дочерних элементов
        self.delete_selected_button.grid(row=0, column=0, sticky='ew')
        self.delete_all_button.grid(row=0, column=1, sticky='ew')
        self.columnconfigure((0,1), weight=1) # Растягиваем обе кнопки по ширине фрейма

        # Привязываем функцию к событию ListboxSelect
        self.listbox_frame.listbox.bind('<<ListboxSelect>>', lambda event: self.update_buttons_state())
        
        # Вызываем функцию для установки начального состояния кнопок
        self.update_buttons_state()


    def update_buttons_state(self):
        if self.listbox_frame.listbox.size() == 0:
            self.delete_selected_button.config(state='disabled')
            self.delete_all_button.config(state='disabled')
        else:
            self.delete_selected_button.config(state='normal')
            self.delete_all_button.config(state='normal')

    
    def delete_selected_ips(self):
        def delete():
            selected_indices = self.listbox_frame.listbox.curselection()
            for index in reversed(selected_indices):
                self.listbox_frame.listbox.delete(index)
            # После удаления элементов обновляем состояние кнопок
            self.update_buttons_state()
            if self.start_frame:
                self.start_frame.update_buttons_state()
        return delete

    def delete_all_ips(self):
        def delete():
            self.listbox_frame.listbox.delete(0, 'end')
            # После удаления элементов обновляем состояние кнопок
            self.update_buttons_state()
            if self.start_frame:
                self.start_frame.update_buttons_state()
        return delete


class IpListFrame(tk.Frame):
    def __init__(self, master=None, **kwargs) -> None:
        super().__init__(master, **kwargs)

        # Инициализация
        self.scrollbar = tk.Scrollbar(self, orient='vertical')
        self.listbox = tk.Listbox(self, selectmode=tk.MULTIPLE, yscrollcommand=self.scrollbar.set)

        # Отображение дочерних элементов
        self.listbox.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        self.scrollbar.config(command=self.listbox.yview) # Привязываем ip_list_scrollbar к управлению ip_list_listbox


class TimeFrame(tk.Frame):
    def __init__(self, master=None, listbox_frame=None, **kwargs) -> None:
        super().__init__(master, **kwargs)

        # Ссылка на список IP
        self.listbox_frame = listbox_frame

        # Инициализация переменных
        self.set_time_var = tk.IntVar(value=1)
        self.analyse_time_var = tk.IntVar()
        self.summary_time_var = tk.IntVar()

        # Инициализация дочерних элементов
        self.set_time_label = tk.Label(self, text='Время сбора данных (в сек.):')
        self.analyse_time_label = tk.Label(self, text='Время анализа данных:')
        self.summary_time_label = tk.Label(self, text='Время всего процесса:')
        self.set_time_entry = tk.Entry(self, width=5, textvariable=self.set_time_var, validate='key', validatecommand=(self.register(validate_number), '%P'))
        self.analyse_time_info = tk.Label(self, textvariable=self.analyse_time_var)
        self.summary_time_info = tk.Label(self, textvariable=self.summary_time_var)

        # Отображение дочерних элементов
        self.set_time_label.grid(row=0, column=0, sticky='w', padx=(0,10))
        self.set_time_entry.grid(row=0, column=1, sticky='w')
        self.analyse_time_label.grid(row=1, column=0, sticky='w', padx=(0,10))
        self.analyse_time_info.grid(row=1, column=1, sticky='w')
        self.summary_time_label.grid(row=2, column=0, sticky='w', padx=(0,10))
        self.summary_time_info.grid(row=2, column=1, sticky='w')
        self.columnconfigure(1, weight=1) # Растягиваем второй столбец по ширине фрейма

        # Обновление меток при изменении значения в поле ввода
        self.set_time_var.trace_add('write', lambda *_: self.update_times())

    def update_times(self, *args):
        try:
            set_time = int(self.set_time_var.get())
            analyse_time = ceil(set_time*(0.012+0.00084*self.listbox_frame.listbox.size()))
            summary_time = set_time + analyse_time
            self.analyse_time_var.set(seconds_to_hms(analyse_time))
            self.summary_time_var.set(seconds_to_hms(summary_time))
        except TclError:
            self.analyse_time_var.set("Нет данных")
            self.summary_time_var.set("Нет данных")


class FilePathFrame(tk.Frame):
    def __init__(self, master=None, **kwargs) -> None:
        super().__init__(master, **kwargs)

        # Инициализация дочерних элементов
        self.pcapng_label = tk.Label(self, text='Путь к файлу .pcapng:')
        self.pcapng_entry = tk.Entry(self, validate='focusout')
        self.csv_label = tk.Label(self, text='Путь к файлу .csv:')
        self.csv_entry = tk.Entry(self, validate='focusout')

        # Привязываем валидацию к введенному в поле ввода
        self.pcapng_entry.bind('<KeyRelease>', lambda event, entry=self.pcapng_entry: validate_path(entry))
        self.csv_entry.bind('<KeyRelease>', lambda event, entry=self.csv_entry: validate_path(entry))

        # Расположение дочерних элементов
        self.pcapng_label.grid(row=0, column=0, sticky='w', padx=(0,10))
        self.pcapng_entry.grid(row=0, column=1, sticky='we')
        self.csv_label.grid(row=1, column=0, sticky='w')
        self.csv_entry.grid(row=1, column=1, sticky='we')
        self.columnconfigure(1, weight=1) # Растягиваем второй столбец по ширине фрейма

    def fill_empty_entries(self, text: str):
        if not self.pcapng_entry.get():
            self.pcapng_entry.insert(0,text)
        if not self.csv_entry.get():
            self.csv_entry.insert(0,text)
        

class StartAnalyseFrame(tk.Frame):
    def __init__(self, master=None, listbox_frame=None, time_frame=None, file_path_frame=None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.master = master

        # Инициализация ссылок на дочерние элементы
        self.listbox_frame = listbox_frame
        self.time_frame = time_frame
        self.file_path_frame = file_path_frame

        # Инициализация дочерних элементов
        self.analyse_new = tk.Button(self, text='Запустить запись и анализ новых данных', command=lambda: self.start_analysis())
        self.analyse_pcapng = tk.Button(self, text='Запустить анализ данных из .pcapng', command=lambda: self.start_analysis(False, True))
        self.analyse_csv = tk.Button(self, text='Запустить анализ данных из .csv', command=lambda: self.start_analysis(True, True))

        # Расположение дочерних элементов
        self.analyse_new.pack(fill='x')
        self.analyse_pcapng.pack(fill='x')
        self.analyse_csv.pack(fill='x')

        # Привязываем функцию к событиям изменения
        self.time_frame.set_time_var.trace_add('write', self.update_buttons_state)
        self.file_path_frame.pcapng_entry.bind('<KeyRelease>', self.update_buttons_state)
        self.file_path_frame.csv_entry.bind('<KeyRelease>', self.update_buttons_state)

        # Вызываем функцию для установки начального состояния кнопок
        self.update_buttons_state()

    def update_buttons_state(self, *_):
        try:
            valid_time = validate_number(self.time_frame.set_time_var.get())
        except TclError:
            valid_time = False

        # Проверяем условия для активации кнопок
        if (self.listbox_frame.listbox.size() != 0 and 
            valid_time and 
            validate_path(self.file_path_frame.pcapng_entry) and 
            validate_path(self.file_path_frame.csv_entry)):
            self.analyse_new.config(state='normal')
            self.analyse_pcapng.config(state='normal')
            self.analyse_csv.config(state='normal')
        else:
            self.analyse_new.config(state='disabled')
            self.analyse_pcapng.config(state='disabled')
            self.analyse_csv.config(state='disabled')

    def start_analysis(self, skip_sniffing = False, skip_converting = False):
        
        senders_ips = list(self.listbox_frame.listbox.get(0, tk.END))
        parsing_time = int(self.time_frame.set_time_entry.get())
        pcapng_path = str(self.file_path_frame.pcapng_entry.get())+'/bpt.pcapng'
        csv_path = str(self.file_path_frame.csv_entry.get())+'/bpt.csv'
        
        self.master.master.withdraw()  # Скрыть основное окно
        loading_page = LoadingPage(self.master.master)
        # loading_page.grab_set()
        self.master.master.update()
        
        if not skip_sniffing:
            sniff_data(parsing_time, pcapng_path)
        if not skip_converting:
            if os.path.isfile(pcapng_path) == False:
                loading_page.destroy()
                self.master.master.deiconify()
                show_warning('Файл bpt.pcapng не найден')
                return
            pcapng_to_csv(pcapng_path, csv_path)
        if os.path.isfile(csv_path) == False:
            loading_page.destroy()
            self.master.master.deiconify()
            show_warning('Файл bpt.csv не найден')
            return
        try:
            epoch_start, epoch_end = get_epoch(csv_path)
        except StopIteration:
            loading_page.destroy()
            self.master.master.deiconify()
            show_no_data_warning()
            return
        try:
            os.mkdir('./plots')
        except FileExistsError:
            pass
        create_all_plots(senders_ips, csv_path, epoch_start, epoch_end)

        loading_page.destroy()
        self.master.master.deiconify()


class MainPage:
    def __init__(self) -> None:

        self.logo_text = r"""
            |    _)  |         /\           
             _ \  |   _|      /  \          
   /\      _.__/__|_\__|_____/    \         
__/  \    /          |        |    \        
      \  /      _ \  |   _ \   _|   \_v.1.2_
       \/      .__/ _| \___/ \__|           
              _|                            
"""

        self.root = tk.Tk(className='Bitplot')
        self.root.title('Bitplot')
        self.custom_font = font.Font(family='Arial', size=11)
        self.root.option_add('*Font', self.custom_font)

        # Инициализация дочерних элементов
        self.main_frame = tk.Frame(self.root)
        self.logo_label = tk.Label(self.main_frame, text=self.logo_text, font=('Courier', 12))
        self.ip_list_frame = IpListFrame(self.main_frame)
        self.delete_ip_frame = DeleteIpsFrame(self.main_frame, listbox_frame=self.ip_list_frame)
        self.add_ip_frame = AddIpFrame(self.main_frame, listbox_frame=self.ip_list_frame, delete_frame=self.delete_ip_frame)
        self.time_frame = TimeFrame(self.main_frame, listbox_frame=self.ip_list_frame)
        self.file_path_frame = FilePathFrame(self.main_frame)
        self.start_analyse_frame = StartAnalyseFrame(self.main_frame, listbox_frame=self.ip_list_frame, time_frame=self.time_frame, file_path_frame=self.file_path_frame)
        self.delete_ip_frame.start_frame = self.start_analyse_frame
        self.add_ip_frame.start_frame = self.start_analyse_frame

        # Отображение дочерних элементов
        self.main_frame.pack(fill='both', padx='20', pady='20', expand=True)
        self.logo_label.pack(fill='x')
        self.add_ip_frame.pack(fill='x', pady=(0,5))
        self.ip_list_frame.pack(fill='both', expand=True)
        self.delete_ip_frame.pack(fill='x',pady=(5,0))
        
        Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=20)
        self.time_frame.update_times()
        self.time_frame.pack(fill='x')
        
        Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=20)
        self.file_path_frame.pack(fill='x')
        self.file_path_frame.fill_empty_entries('/tmp')
        
        Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=20)
        self.start_analyse_frame.pack(fill='x')


if __name__ == '__main__':
    pass