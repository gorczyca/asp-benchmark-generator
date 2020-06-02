from view.vertical_notebook.vertical_notebook_tab import VerticalNotebookTab

TAB_NAME = 'Associacions'


class AssociationsTab(VerticalNotebookTab):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        VerticalNotebookTab.__init__(self, parent, parent_notebook, TAB_NAME, *args, **kwargs)