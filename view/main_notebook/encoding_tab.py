from view.vertical_notebook.vertical_notebook import VerticalNotebook
from view.tab import Tab

TAB_NAME = 'Encoding'


class EncodingTab(Tab):
    def __init__(self, parent, *args, **kwargs):
        Tab.__init__(self, parent, TAB_NAME, *args, **kwargs)

        # main_notebook
        self.vertical_notebook = VerticalNotebook(self)


