from view.abstract.tab import Tab

TAB_NAME = 'Ports'


class PortsTab(Tab):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        Tab.__init__(self, parent_notebook, TAB_NAME, *args, **kwargs)