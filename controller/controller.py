from model.model import Model
from view.view import View
from pubsub import pub
from controller import actions


class Controller:
    def __init__(self, main_window):
        self.model = Model()
        self.view = View(main_window)

    def __get_hierarchy(self, callback):
        callback(self.model.get_hierarchy())

    def text(self, callback):
        callback('from controller')



    def __register_listeners(self):
        #pub.subscribe(self.__get_hierarchy, actions.BUTTON_CLICK)
        pub.subscribe(self.text, actions.BUTTON_CLICK)

    def run(self):
        self.__register_listeners()
        self.view.mainloop()

