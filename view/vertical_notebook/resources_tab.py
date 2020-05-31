from view.tab import Tab

TAB_NAME = 'Resources'

class ResourcesTab(Tab):
    def __init__(self, parent):
        Tab.__init__(self, parent, TAB_NAME)