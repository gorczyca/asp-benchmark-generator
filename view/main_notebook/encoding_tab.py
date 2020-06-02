from view.vertical_notebook.vertical_notebook import VerticalNotebook
from view.c_tab import CTab

TAB_NAME = 'Encoding'


class EncodingTab(CTab):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        CTab.__init__(self, parent, parent_notebook, TAB_NAME, *args, **kwargs)




