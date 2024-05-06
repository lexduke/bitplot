import tkinter as tk
from tkinter import messagebox
from subprocess import Popen, PIPE

class PasswordWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Введите пароль")
        self.geometry("300x100")
        self.resizable(False, False)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=10)
        self.confirm_button = tk.Button(self, text="Подтвердить", command=self.confirm_password)
        self.confirm_button.pack()

    def validate_password(self, password):
        cmd = 'echo "Password is valid"'
        proc = Popen(['pkexec', 'bash', '-c', cmd], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        proc.communicate(password.encode())
        return_code = proc.returncode
        return True if return_code == 0 else False


    def confirm_password(self):
        password = self.password_entry.get()
        if self.validate_password(password):
            self.withdraw()  # Скрыть окно вместо уничтожения
            # self.master.start_long_process()
            print("GOOD")
        else:
            messagebox.showerror("Ошибка", "Неверный пароль")

if __name__ == "__main__":
    app = PasswordWindow()
    app.mainloop()