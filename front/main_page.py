import os
import tkinter as tk
from tkinter import font
import re
from tkinter.ttk import Separator
from _tkinter import TclError
from math import ceil


logo_text = """
            |    _)  |         /\         
             _ \  |   _|      /  \        
   /\      _.__/__|_\__|_____/    \       
__/  \    /          |        |    \      
      \  /      _ \  |   _ \   _|   \_____
       \/      .__/ _| \___/ \__|         
              _|                          
"""


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
        self.entry.bind('<KeyRelease>', self.validate_entry)

    def validate_ip(self, text):
        # Проверка формата IP-адреса
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){0,3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?){0,1}$'
        return True if re.match(pattern, text) or text == "" else False

    def validate_entry(self, event):
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
        self.set_time_label = tk.Label(self, text='Время сбора данных (в секундах):')
        self.analyse_time_label = tk.Label(self, text='Время анализа данных (в секундах):')
        self.summary_time_label = tk.Label(self, text='Время всего процесса (в секундах):')
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
            self.analyse_time_var.set(analyse_time)
            self.summary_time_var.set(summary_time)
        except TclError:
            self.analyse_time_var.set(0)
            self.summary_time_var.set(0)


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
        

class StartAnalyseFrame(tk.Frame):
    def __init__(self, master=None, add_frame=None, listbox_frame=None, delete_frame=None, time_frame=None, file_path_frame=None, **kwargs) -> None:
        super().__init__(master, **kwargs)

        # Инициализация ссылок на дочерние элементы
        self.add_frame = add_frame
        self.listbox_frame = listbox_frame
        self.delete_frame = delete_frame
        self.time_frame = time_frame
        self.file_path_frame = file_path_frame

        # Инициализация дочерних элементов
        self.analyse_new = tk.Button(self, text='Запустить запись и анализ новых данных', command=None)
        self.analyse_pcapng = tk.Button(self, text='Запустить анализ данных из .pcapng', command=None)
        self.analyse_csv = tk.Button(self, text='Запустить анализ данных из .csv', command=None)

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


# Основное окно
root = tk.Tk(className='Bitplot')
root.title('Bitplot')
custom_font = font.Font(family='Arial', size=11)
root.option_add('*Font', custom_font)

# Инициализация дочерних элементов
main_frame = tk.Frame(root)
logo_label = tk.Label(main_frame, text=logo_text, font=('Courier', 12))
ip_list_frame = IpListFrame(main_frame)
delete_ip_frame = DeleteIpsFrame(main_frame, listbox_frame=ip_list_frame)
add_ip_frame = AddIpFrame(main_frame, listbox_frame=ip_list_frame, delete_frame=delete_ip_frame)
time_frame = TimeFrame(main_frame, listbox_frame=ip_list_frame)
file_path_frame = FilePathFrame(main_frame)
start_analyse_frame = StartAnalyseFrame(main_frame, add_frame=add_ip_frame, listbox_frame=ip_list_frame, delete_frame=delete_ip_frame, time_frame=time_frame, file_path_frame=file_path_frame)
delete_ip_frame.start_frame = start_analyse_frame
add_ip_frame.start_frame = start_analyse_frame

# Отображение дочерних элементов
main_frame.pack(fill='both', padx='20', pady='20', expand=True)
logo_label.pack(fill='x')
add_ip_frame.pack(fill='x', pady=(0,5))
ip_list_frame.pack(fill='both', expand=True)
delete_ip_frame.pack(fill='x',pady=(5,0))

Separator(main_frame, orient='horizontal').pack(fill='x', pady=20)

time_frame.update_times()
time_frame.pack(fill='x')

Separator(main_frame, orient='horizontal').pack(fill='x', pady=20)

file_path_frame.pack(fill='x')

Separator(main_frame, orient='horizontal').pack(fill='x', pady=20)

start_analyse_frame.pack(fill='x')

root.mainloop()