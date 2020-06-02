import tkinter as tk


class CFrame(tk.Frame):
    def __init__(self, parent, parent_frame, *args, **kwargs):
        tk.Frame.__init__(self, parent_frame, *args, **kwargs)

        self.controller = parent.controller
        self.parent_frame = parent_frame



