from view.abstract.tab import Tab

TAB_NAME = 'Encoding'


class EncodingTab(Tab):
    def __init__(self, parent_notebook):
        Tab.__init__(self, parent_notebook, TAB_NAME)
        # TODO: this class is unnecessary?
        self._frame.rowconfigure(0, weight=1)
        self._frame.columnconfigure(0, weight=1)

    @property
    def frame(self):
        return self._frame




