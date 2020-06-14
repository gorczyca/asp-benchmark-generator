from typing import Optional

from model.component import Component
from view.hierarchy_tree import HierarchyTree
from view.vertical_notebook.vertical_notebook_tab import VerticalNotebookTab
from view.c_frame import CFrame

TAB_NAME = 'Resources'


class ResourcesTab(VerticalNotebookTab, CFrame):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        VerticalNotebookTab.__init__(self, parent_notebook, TAB_NAME, *args, **kwargs)
        CFrame.__init__(self, parent, parent_notebook)

        self.__hierarchy_tree: Optional[HierarchyTree] = None
        self.__selected_component: Optional[Component]

    def _create_widgets(self):
        pass

    def _setup_layout(self):
        pass

    def _subscribe_to_listeners(self):
        pass

