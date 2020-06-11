import tkinter as tk
from tkinter import ttk, messagebox
from view.c_frame import CFrame
from pubsub import pub
import actions
from view import style
from exceptions import HierarchyStringError
from view.common_callbacks import select_all_text
import model.helpers.string_converter as string_converter

EDIT_HIERARCHY_WINDOW_NAME = 'Edit hierarchy'
EDIT_HIERARCHY_WINDOW_SIZE = '800x800'
EDIT_HIERARCHY_LABEL_TEXT = 'Input hierarchy of view.\n("Tab" means subcomponent of component above.)'


# TODO: 1 czy na pewno potrzebuję, żeby wszystko było 'self'

class CreateHierarchyWindow(CFrame):
    def __init__(self, parent, parent_frame, callback, *args, **kwargs):
        CFrame.__init__(self, parent, parent_frame)

        self.__callback = callback
        self.window = tk.Toplevel(self.parent_frame, *args, **kwargs)
        self.window.grab_set()

        self.window.title(EDIT_HIERARCHY_WINDOW_NAME)
        self.window.geometry(EDIT_HIERARCHY_WINDOW_SIZE)

        self.label = ttk.Label(self.window, text=EDIT_HIERARCHY_LABEL_TEXT, anchor=tk.W)
        self.label.grid(row=0, column=0, sticky='nswe', padx=5, pady=5)

        self.text_frame = tk.Frame(self.window)
        self.x_scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.HORIZONTAL)
        self.x_scrollbar.grid(row=1, column=0, sticky='swe')

        self.y_scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL)
        self.y_scrollbar.grid(row=0, column=1, sticky='nse')

        self.text = tk.Text(self.text_frame, wrap=tk.NONE, font=style.FONT_BOLD,
                            xscrollcommand=self.x_scrollbar.set, yscrollcommand=self.y_scrollbar.set)

        self.text.grid(column=0, row=0, sticky='nswe')
        self.text.focus()
        self.text.mark_set(tk.INSERT, 1.0)
        self.text.bind('<Control-a>', select_all_text)

        if self.controller.model.hierarchy:
            hierarchy_string = string_converter.hierarchy_to_string(self.controller.model.hierarchy)
            self.text.insert(1.0, hierarchy_string)

        self.text_frame.columnconfigure(0, weight=1)
        self.text_frame.rowconfigure(0, weight=1)

        self.x_scrollbar.config(command=self.text.xview)
        self.y_scrollbar.config(command=self.text.yview)

        self.text_frame.grid(row=1, column=0, columnspan=2, sticky='nswe')

        self.buttons_frame = tk.Frame(self.window)
        self.ok_button = ttk.Button(self.buttons_frame, text='Ok', command=self.__ok)
        self.ok_button.grid(row=0, column=0, sticky='e', pady=5)
        self.cancel_button = ttk.Button(self.buttons_frame, text='Cancel', command=self.window.destroy)
        self.cancel_button.grid(row=0, column=1, sticky='w', pady=5)

        self.buttons_frame.grid(row=2, column=0, columnspan=2, sticky='nswe')
        self.buttons_frame.columnconfigure(0, weight=1)
        self.buttons_frame.columnconfigure(1, weight=1)

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)

    def __ok(self):
        self.window.grab_release()
        hierarchy_string = self.text.get(1.0, tk.END)
        try:
            hierarchy = string_converter.string_to_hierarchy(hierarchy_string)
            self.controller.model.hierarchy = hierarchy
            pub.sendMessage(actions.HIERARCHY_CREATED)
            pub.sendMessage(actions.MODEL_CHANGED)
            self.window.destroy()
        except HierarchyStringError as e:
            messagebox.showerror('Error', e.message)



