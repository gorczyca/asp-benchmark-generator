import tkinter as tk
from view.style import CustomTheme
from view.menu import Menu
from view.main_notebook.main_notebook import MainNotebook

WINDOW_TITLE = 'Benchmark Generator'

# TODO: wszystkie komponenty tu upchnąc wieksze ??
class View(tk.Frame):
    def __init__(self, main_window, *args, **kwargs):
        tk.Frame.__init__(self, main_window, *args, **kwargs)
        self.frame = main_window
        self.frame.title(WINDOW_TITLE)
        # self.frame.geometry(WINDOW_SIZE)
        self.__setup_layout()

    def __setup_layout(self):
        CustomTheme().use()
        self.__menu = Menu(self)
        self.__main_notebook = MainNotebook(self)

