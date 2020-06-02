from view.c_tab import CTab

TAB_HEIGHT = 720
TAB_WIDTH = 1080


class VerticalNotebookTab(CTab):
    def __init__(self, parent, parent_frame, tab_name, *args, **kwargs):
        CTab.__init__(self, parent, parent_frame, tab_name, height=TAB_HEIGHT, width=TAB_WIDTH, *args, **kwargs)

