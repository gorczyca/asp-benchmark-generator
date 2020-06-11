from view.tab import Tab

TAB_NAME = 'Encoding'


class EncodingTab(Tab):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        Tab.__init__(self, parent_notebook, TAB_NAME, *args, **kwargs)




