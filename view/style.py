from tkinter import ttk

# ('clam', 'alt', 'default', 'classic'
PARENT_THEME = 'clam'
# PARENT_THEME = 'radiance'
STYLE_NAME = 'CUSTOM_STYLE'


class CustomTheme(ttk.Style):
    def __init__(self, master=None, *args, **kwargs):
        ttk.Style.__init__(self, master,  *args, **kwargs)

        # font=('URW Gothic L','40','bold')
        self.style = ttk.Style(master)
        self.style.theme_create(STYLE_NAME, parent=PARENT_THEME, settings={
            "Vertical.TNotebook": {"configure": {"tabmargins": [10, 50, 10, 0], 'tabposition': 'wns'}},
            "Vertical.TNotebook.Tab": {"configure": {'width': 12, 'padding': [50, 50], 'borderwidth': 3, 'focuscolor': "#dd4814"}, # usuwa tę brzydką ramkę
                                       "map": {"background": [("selected", "#dF4F1F")], "expand": [("selected", [1, 1, 1, 0])]}},
            'Main.TNotebook.Tab': {'configure': {'width': 10, 'padding': [5, 5]}},
            'Custom.Treeview': {'configure': {'highlightthickness': 0, 'bd': 0, 'font': ('Arial', 11)}},
            'Custom.Treeview.Heading': {'configure': {'font': ('Arial', 13, 'bold')}},
            })

        # self.style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders

    def use(self):
        self.style.theme_use(STYLE_NAME)