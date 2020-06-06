from model.model import Model
from view.view import View
from pubsub import pub
from controller import actions


class Controller:
    def __init__(self, main_window):
        self.model = Model()
        self.view = View(self, main_window)
        # state
        self.file = None
        self.saved = True

        pub.subscribe(self.__unsaved_changes, actions.MODEL_CHANGED)

    def __get_hierarchy(self, callback):
        callback(self.model.get_hierarchy())

    def run(self):
        self.view.mainloop()

    def __unsaved_changes(self):
        self.saved = False

