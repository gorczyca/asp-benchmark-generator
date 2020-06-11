import tkinter as tk

from controller import Controller


if __name__ == "__main__":
    main_window = tk.Tk()
    Controller(main_window).run()
