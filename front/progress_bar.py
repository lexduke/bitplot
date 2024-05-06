import tkinter as tk

class LoadingScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Загрузка...")
        self.geometry("300x100")
        self.resizable(False, False)
        self.loading_label = tk.Label(self, text="Выполняется загрузка, пожалуйста, подождите...")
        self.loading_label.pack(pady=10)

def show_loading_screen():
    loading_screen = LoadingScreen()
    loading_screen.mainloop()