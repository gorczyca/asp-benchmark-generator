import tkinter as tk
from controller.controller import Controller
from ttkthemes import ThemedTk

# requirements
# tkinter
# pypubsub
# tttkthemes

from view.style import PARENT_THEME


if __name__ == "__main__":
    main_window = tk.Tk()
    # main_window = ThemedTk(theme=PARENT_THEME)
    Controller(main_window).run()
