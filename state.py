from typing import Optional, TextIO

from model.model import Model


# class Borg:
#     _shared_state = {}
#
#     def __init__(self):
#         self.__dict__ = self._shared_state
#
#
# class State(Borg):
#     def __init__(self):
#         Borg.__init__(self)
#         # self.val = arg
#         self.model: Model = Model()
#         self.file: Optional[TextIO] = None
#         self.is_saved: bool = True

    # def __str__(self): return self.val

class State:
    class __State:
        def __init__(self):
            self.model: Model = Model()
            self.file: Optional[TextIO] = None
            self.is_saved: bool = True

        # def __str__(self):
        #     return repr(self) + self.val

    instance = None

    def __new__(cls):
        if not State.instance:
            State.instance = State.__State()
        return State.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)
