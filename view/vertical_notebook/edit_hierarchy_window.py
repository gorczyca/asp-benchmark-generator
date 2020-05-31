import tkinter as tk
from tkinter import ttk, messagebox
from data.component import Component

EDIT_HIERARCHY_WINDOW_NAME = 'Edit hierarchy'
EDIT_HIERARCHY_WINDOW_SIZE = '800x800'
EDIT_HIERARCHY_LABEL_TEXT = 'Input hierarchy of view. \n"Tab" means subcomponent of component above.'

CHILD_SYMBOL = '\t'
NUMBER_OF_SPACES_EQUAL_TO_TAB = 4


# TODO: 1 czy na pewno potrzebuję, żeby wszystko było 'self'
# TODO: 2 ogarnąć jak zrobić, żeby przycisk cancel nie zjeżdzał


class EditHierarchyWindow(tk.Frame):
    def __init__(self, parent, callback, *args, **kwargs):
        tk.Frame.__init__(self, parent._frame, *args, **kwargs)
        self.parent = parent

        self.__callback = callback

        self._window = tk.Toplevel(self.parent._frame)

        self._window.grab_set()

        self._window.title(EDIT_HIERARCHY_WINDOW_NAME)
        self._window.geometry(EDIT_HIERARCHY_WINDOW_SIZE)

        self.__label = tk.Label(self._window, text=EDIT_HIERARCHY_LABEL_TEXT)
        self.__label.grid(row=0, column=0)

        self.__text_frame = tk.Frame(self._window)
        self.__x_scrollbar = ttk.Scrollbar(self.__text_frame, orient=tk.HORIZONTAL)
        self.__x_scrollbar.grid(row=1, column=0, sticky='swe')  # col?

        self.__y_scrollbar = ttk.Scrollbar(self.__text_frame, orient=tk.VERTICAL)
        self.__y_scrollbar.grid(row=0, column=1, sticky='nse')  # row ?

        self.__text = tk.Text(self.__text_frame, wrap=tk.NONE,
                              xscrollcommand=self.__x_scrollbar.set,
                              yscrollcommand=self.__y_scrollbar.set)
        self.__text.grid(column=0, row=0, sticky='nswe')
        self.__text.focus()

        self.__text_frame.columnconfigure(0, weight=1)
        self.__text_frame.rowconfigure(0, weight=1)

        self.__x_scrollbar.config(command=self.__text.xview)
        self.__y_scrollbar.config(command=self.__text.yview)

        self.__text_frame.grid(row=1, column=0, columnspan=2, sticky='nswe')

        self.__buttons_frame = tk.Frame(self._window)
        self.__ok_button = tk.Button(self.__buttons_frame, text='Ok', command=self.__ok)
        self.__ok_button.grid(row=0, column=0)
        self.__cancel_button = tk.Button(self.__buttons_frame, text='Cancel', command=self._window.destroy)
        self.__cancel_button.grid(row=0, column=1)

        self.__buttons_frame.grid(row=2, column=0, columnspan=2, sticky='nswe')

        self._window.columnconfigure(0, weight=1)
        self._window.rowconfigure(1, weight=1)

    def __ok(self):
        self._window.grab_release()
        hierarchy_string = self.__text.get(1.0, tk.END)
        try:
            self.parent.hierarchy = EditHierarchyWindow.string_to_hierarchy(hierarchy_string)
            self._window.destroy()
            self.__callback()
        except Exception as e: # TODO: lepiej tam
            messagebox.showerror('Error', str(e))

    @staticmethod
    def set_leaves(hierarchy):
        for cmp in hierarchy:
            if not cmp.children:
                cmp.set_leaf()
            else:
                EditHierarchyWindow.set_leaves(cmp.children)

    @staticmethod
    def extract_tabs(line):
        tab_count = 0
        for letter in line:
            if letter != CHILD_SYMBOL:
                break
            else:
                tab_count += 1
        return tab_count, line.split()[0]

    @staticmethod
    def string_to_hierarchy(hierarchy_string):
        hierarchy_string = hierarchy_string.replace(' ' * NUMBER_OF_SPACES_EQUAL_TO_TAB,
                                                    CHILD_SYMBOL)  # make sure N spaces are converted to '\t'
        hierarchy = []
        _last_on_level = []
        for line in hierarchy_string.split('\n'):
            if not line or line.isspace():  # if entire line contains only spaces, ignore it
                continue
            level, component_name = EditHierarchyWindow.extract_tabs(line)
            if len(_last_on_level) < level:
                raise Exception(f'Cannot create a child of non-existing component.\n'
                                f'Check number of tabs in component: "{component_name}" and its ancestor.')

            component = Component(component_name, level)

            if len(_last_on_level) > level:
                _last_on_level[level] = component  # there already exists a level
            else:
                _last_on_level.append(component)  # add level above

            if level != 0:
                _last_on_level[level - 1].children.append(component)
            else:
                hierarchy.append(component)
        EditHierarchyWindow.set_leaves(hierarchy)
        return hierarchy

    @staticmethod
    def hierarchy_to_string(hierarchy):
        pass




