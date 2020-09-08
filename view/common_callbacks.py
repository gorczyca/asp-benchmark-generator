import tkinter as tk


def select_all_text(event):
    event.widget.tag_add(tk.SEL, 1.0, tk.END)
    event.widget.mark_set(tk.INSERT, 1.0)
    event.widget.see(tk.INSERT)
    return 'break'


def select_all_entry(event):
    event.widget.select_range(0, tk.END)
    event.widget.icursor(tk.END)
    return 'break'
