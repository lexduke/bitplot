import tkinter as tk

class LoadingPage(tk.Toplevel):
    def __init__(self, master = None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.master = master
        self.title("Загрузка")
        self.loading_label = tk.Label(self, text="Идет загрузка, подождите...")
        self.loading_label.pack(padx=20, pady=20)

    def close(self):
        self.destroy()
        self.master.deiconify()


if __name__ == "__main__":
    pass