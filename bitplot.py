from front.warnings import show_startup_warning
from front.main_page import MainPage

if __name__ == '__main__':
    show_startup_warning()
    main_page = MainPage()
    main_page.root.mainloop()