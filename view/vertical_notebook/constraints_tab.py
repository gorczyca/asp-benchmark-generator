from view.vertical_notebook.vertical_notebook_tab import VerticalNotebookTab

TAB_NAME = 'Constraints'


class ConstraintsTab(VerticalNotebookTab):
    def __init__(self, parent):
        VerticalNotebookTab.__init__(self, parent, TAB_NAME)