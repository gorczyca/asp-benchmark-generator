from view.abstract import HasCommonSetup, Tab

TAB_NAME = 'Encoding'


class EncodingTab(Tab,
                  HasCommonSetup):
    def __init__(self, parent_notebook):
        Tab.__init__(self, parent_notebook, TAB_NAME)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        pass

    def _setup_layout(self) -> None:
        self._frame.rowconfigure(0, weight=1)
        self._frame.columnconfigure(0, weight=1)

    @property
    def frame(self):
        return self._frame




