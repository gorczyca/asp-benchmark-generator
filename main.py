# Use Tkinter for python 2, tkinter for python 3
import tkinter as tk
from tkinter import ttk
from view import Menu, MainNotebook
from style import CustomTheme   
  

WINDOW_TITLE = 'Benchmark Generator'


class Root:
    def __init__(self, hierarchy=None):
        self.hierarchy = hierarchy


class MainApplication(tk.Frame):
    def __init__(self, window, *args, **kwargs):
        tk.Frame.__init__(self, window, *args, **kwargs)
        self.frame = window

        self.root = Root()


        CustomTheme().use()

        self.frame.title(WINDOW_TITLE)
        #self.frame.geometry(WINDOW_SIZE)

        # main_notebook
        self.menu = Menu(self)
        self.main_notebook = MainNotebook(self)


if __name__ == "__main__":
    window = tk.Tk()
    MainApplication(window).grid(row=0, column=0, sticky='nswe')
    window.mainloop()
