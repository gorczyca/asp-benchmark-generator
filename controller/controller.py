from model.model import Model
from view.view import View


class Controller:
    def __init__(self, main_window):
        self.model = Model()
        self.view = View(self, main_window)

    def __get_hierarchy(self, callback):
        callback(self.model.get_hierarchy())

    def __register_listeners(self):
        pass

    def run(self):
        self.__register_listeners()
        self.view.mainloop()

