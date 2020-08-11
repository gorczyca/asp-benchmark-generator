from settings import Settings
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.window import Window
from view.generate_frame import GenerateFrame

WINDOW_TITLE = 'Generate logic program...'

GENERATED_FILE_SUFFIX = 'gen'

WINDOW_WIDTH_RATIO = 0.4
WINDOW_HEIGHT_RATIO = 0.8


class GenerateWindow(HasCommonSetup,
                     Window):
    def __init__(self, parent_frame, callback):
        self.__state = State()
        self.__callback = callback
        self.__settings = Settings.get_settings()

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__generate_frame = GenerateFrame(self._window, self.__settings, self.__state)

    def _setup_layout(self) -> None:
        self.__generate_frame.grid(row=0, column=0)
        self._set_geometry(height_ratio=WINDOW_HEIGHT_RATIO, width_ratio=WINDOW_WIDTH_RATIO)
