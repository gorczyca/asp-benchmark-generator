import tkinter as tk

# TODO: make abstract and add: create_widgets, setup_layout, subscribe to events methods


class CFrame(tk.Frame):
    def __init__(self, parent, parent_frame):
        tk.Frame.__init__(self, parent_frame)

        self.controller = parent.controller
        self.parent_frame = parent_frame



