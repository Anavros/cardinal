
from vispy import app

# automatically updates
# might do something fancy later, but solid 60fps for now
class AutoCanvas(app.Canvas):
    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        self.timer = app.Timer(connect=self.on_timer)

    def on_timer(self, event):
        self.update()

    def start(self):
        self.show()
        self.timer.start()


class GameState(object):
    def __init__(self, handle, layout, **kwargs):
        self.handle = handle
        self.layout = layout
        for (k, v) in kwargs.items():
            self.__dict__[k] = v


class Game(object):
    def __init__(self, **kwargs):
        self.states = {}
        self.current_state = None
        self.needs_redraw = False
        self.slate = None
        for (k, v) in kwargs.items():
            self.__dict__[k] = v

    def add_state(self, handle, state):
        self.states[handle] = state

    def use(self, handle):
        self.current_state = self.states[handle]
        self.needs_redraw = True
        print("entering {} state".format(handle))

    def get_state(self):
        return self.current_state
