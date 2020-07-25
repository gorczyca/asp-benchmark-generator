import tkinter as tk
from tkinter import ttk, simpledialog, filedialog

from view import style
from view.abstract.has_common_setup import HasCommonSetup

WINDOW_TITLE = 'Welcome'

CONTROL_PAD_Y = 1.5

FRAME_PAD_Y = 10
FRAME_PAD_X = 10

WINDOW_WIDTH_RATIO = 0.25
WINDOW_HEIGHT_RATIO = 0.25


class InitialWindow(HasCommonSetup):
    def __init__(self, parent_frame, callback):
        self.__parent_frame = parent_frame
        self.__callback = callback

        HasCommonSetup.__init__(self)
        self.__set_geometry()

    def _create_widgets(self) -> None:
        self.__window = tk.Toplevel(self.__parent_frame, bg=style.BACKGROUND_COLOR_PRIMARY)
        self.__window.grab_set()
        self.__window.title(WINDOW_TITLE)

        self.__create_new_project_button = ttk.Button(self.__window, text='Create new project',
                                                      command=self.__create_new_project)
        self.__open_project_button = ttk.Button(self.__window, text='Open project',
                                                command=self.__open_project)
        self.__solve_button = ttk.Button(self.__window, text='Solve...', command=self.__solve)

    def __create_new_project(self):
        root_name = simpledialog.askstring('Set root name', 'Enter name of the root component')
        if root_name:
            self.__callback(root_name)
            self.__window.destroy()

    def __open_project(self):
        # TODO: don't repeat yourself (same is in the menu)
        file = filedialog.askopenfile(mode='r', defaultextension=JSON_EXTENSION)
        if file:
            self.controller.file = file
            json = file.read()
            model = json_converter.json_to_model(json)
            self.controller.model = model
            file_name = Menu.__extract_file_name(file.name)
            pub.sendMessage(actions.MODEL_SAVED, file_name=file_name)
            pub.sendMessage(actions.MODEL_LOADED)

    def __solve(self):
        pass

    def _setup_layout(self) -> None:
        pass

    def __set_geometry(self):
        screen_width = self.__window.winfo_screenwidth()
        screen_height = self.__window.winfo_screenheight()
        window_width = round(screen_width * WINDOW_WIDTH_RATIO)
        window_height = round(screen_height * WINDOW_HEIGHT_RATIO)
        x_pos = round((screen_width - window_width) / 2)
        y_pos = round((screen_height - window_height) / 2)
        self.__window.geometry(f'{window_width}x{window_height}+{x_pos}+{y_pos}')

