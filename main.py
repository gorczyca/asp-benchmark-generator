# Use Tkinter for python 2, tkinter for python 3
import tkinter as tk
from tkinter import ttk
from view import Menu, MainNotebook
from style import CustomTheme   
  

WINDOW_TITLE = 'Benchmark Generator'
WINDOW_SIZE = '1080x720'


class MainApplication(tk.Frame):
    def __init__(self, frame, *args, **kwargs):
        tk.Frame.__init__(self, frame, *args, **kwargs)
        self.frame = frame

        CustomTheme().use()

        self.frame.title(WINDOW_TITLE)
        self.frame.geometry(WINDOW_SIZE)

        # main_notebook
        self.menu = Menu(self)
        self.main_notebook = MainNotebook(self)


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).grid(row=0, column=0, sticky='nswe')
    root.mainloop()