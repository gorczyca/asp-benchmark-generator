import tkinter as tk

# from controller.controller import Controller
from view.view import View

if __name__ == '__main__':
    main_window = tk.Tk()
    View(main_window).mainloop()
    #Controller(main_window).run()
