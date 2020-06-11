from view.tab import Tab

TAB_HEIGHT = 720
TAB_WIDTH = 1080


class VerticalNotebookTab(Tab):
    def __init__(self, parent_frame, tab_name, *args, **kwargs):
        Tab.__init__(self, parent_frame, tab_name, height=TAB_HEIGHT, width=TAB_WIDTH, *args, **kwargs)

