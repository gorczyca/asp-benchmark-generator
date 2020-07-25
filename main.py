import tkinter as tk

from view.initial_window import InitialWindow
from view.style import CustomTheme
from view.view import View

if __name__ == '__main__':
    main_window = tk.Tk()
    main_window.withdraw()

    CustomTheme().use()

    InitialWindow(main_window, callback=lambda: View(main_window))
    main_window.mainloop()

