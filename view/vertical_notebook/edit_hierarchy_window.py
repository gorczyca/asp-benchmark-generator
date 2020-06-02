import tkinter as tk
from tkinter import ttk, messagebox
from model.component import Component
from view.c_frame import CFrame

EDIT_HIERARCHY_WINDOW_NAME = 'Edit hierarchy'
EDIT_HIERARCHY_WINDOW_SIZE = '800x800'
EDIT_HIERARCHY_LABEL_TEXT = 'Input hierarchy of view. \n"Tab" means subcomponent of component above.'

CHILD_SYMBOL = '\t'
NEWLINE_SYMBOL = '\n'
NUMBER_OF_SPACES_EQUAL_TO_TAB = 4


# TODO: 1 czy na pewno potrzebuję, żeby wszystko było 'self'

class EditHierarchyWindow(CFrame):
    def __init__(self, parent, parent_frame, callback, *args, **kwargs):
        CFrame.__init__(self, parent, parent_frame, *args, **kwargs)

        self.__callback = callback
        self.window = tk.Toplevel(self.parent_frame)
        self.window.grab_set()

        self.window.title(EDIT_HIERARCHY_WINDOW_NAME)
        self.window.geometry(EDIT_HIERARCHY_WINDOW_SIZE)

        self.label = tk.Label(self.window, text=EDIT_HIERARCHY_LABEL_TEXT)
        self.label.grid(row=0, column=0)

        self.text_frame = tk.Frame(self.window)
        self.x_scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.HORIZONTAL)
        self.x_scrollbar.grid(row=1, column=0, sticky='swe')

        self.y_scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL)
        self.y_scrollbar.grid(row=0, column=1, sticky='nse')

        self.text = tk.Text(self.text_frame, wrap=tk.NONE,
                              xscrollcommand=self.x_scrollbar.set,
                              yscrollcommand=self.y_scrollbar.set)

        self.text.grid(column=0, row=0, sticky='nswe')
        self.text.focus()
        self.text.mark_set(tk.INSERT, 1.0)
        self.text.bind('<Control-a>', EditHierarchyWindow.select_all)

        hierarchy = self.controller.model.get_hierarchy()

        if hierarchy:
            hierarchy_string = EditHierarchyWindow.hierarchy_to_string(hierarchy)
            self.text.insert(1.0, hierarchy_string)

        self.text_frame.columnconfigure(0, weight=1)
        self.text_frame.rowconfigure(0, weight=1)

        self.x_scrollbar.config(command=self.text.xview)
        self.y_scrollbar.config(command=self.text.yview)

        self.text_frame.grid(row=1, column=0, columnspan=2, sticky='nswe')

        self.buttons_frame = tk.Frame(self.window)
        self.ok_button = ttk.Button(self.buttons_frame, text='Ok', command=self.__ok)
        self.ok_button.grid(row=0, column=0, sticky='e')
        self.cancel_button = ttk.Button(self.buttons_frame, text='Cancel', command=self.window.destroy)
        self.cancel_button.grid(row=0, column=1, sticky='w')

        self.buttons_frame.grid(row=2, column=0, columnspan=2, sticky='nswe')
        self.buttons_frame.columnconfigure(0, weight=1)
        self.buttons_frame.columnconfigure(1, weight=1)

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)

    def __ok(self):
        self.window.grab_release()
        hierarchy_string = self.text.get(1.0, tk.END)
        try:
            hierarchy = EditHierarchyWindow.string_to_hierarchy(hierarchy_string)
            self.window.destroy()
            self.__callback(hierarchy)
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
        def __hierarchy_to_string(_hierarchy, _string, _level):
            for cmp in _hierarchy:
                _string += _level * CHILD_SYMBOL + cmp.name + NEWLINE_SYMBOL
                if cmp.children:
                    _string = __hierarchy_to_string(cmp.children, _string, _level + 1)
            return _string
        string = ''
        level = 0
        return __hierarchy_to_string(hierarchy, string, level)

    # TODO: move somewhere global
    @staticmethod
    def select_all(event):
        event.widget.tag_add(tk.SEL, 1.0, tk.END)
        event.widget.mark_set(tk.INSERT, 1.0)
        event.widget.see(tk.INSERT)
        return 'break'



    # TODO: sprawdzanie unikalności stringów



