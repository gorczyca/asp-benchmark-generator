import tkinter as tk

from view import View, InitialWindow
from view.style import CustomTheme


if __name__ == '__main__':
    main_window = tk.Tk()
    main_window.withdraw()

    CustomTheme().use()

    InitialWindow(main_window, callback=lambda: View(main_window))
    main_window.mainloop()

