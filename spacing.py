
import malt
import numpy as np

CONFIG_SYNTAX = [
    "div handle int(x) int(y)",
    "fit handle anchor[top|bottom|left|right|center] int(size)",
    "ele handle int(x) int(y)",
    "pad handle int(x) int(y)",
]


# TODO: come up with a better name
class Interface(object):
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.panels = []

        self.pad_left = 0
        self.pad_right = 0
        self.pad_top = 0
        self.pad_bottom = 0

    def get(self, handle):
        """Returns the first panel found whose handle matches the given string.

        Raises ValueError if the panel is not found."""
        for p in self.panels:
            if p.handle == handle:
                return p
        raise ValueError("Panel '{}' does not exist!".format(handle))

    def add(self, panel):
        for p in self.panels:
            if p.handle == panel.handle:
                raise ValueError("Panel '{}' already exists!".format(panel.handle))
        self.panels.append(panel)

    def at(self, x, y):
        """Return the panel located at (x, y) in logical pixels."""
        for p in self.panels:
            if p.x <= x <= p.w+p.x and p.y <= y <= p.h+p.y:
                return (p, p.at(x, y))


class Panel(object):
    def __init__(self, handle, x_elements, y_elements):
        self.handle = handle
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.pad_left = 0
        self.pad_top = 0
        self.pad_right = 0
        self.pad_bottom = 0
        self.size = 0
        self.anchor = None
        self.elements = [[]]
        self.shape = (x_elements, y_elements)
        self.element_w = 0
        self.element_h = 0

    def at(self, x, y):
        pass


def create(config_file, width, height):
    gui = Interface(width, height)
    for args in malt.load(config_file, CONFIG_SYNTAX):
        if args == 'div':
            gui.add(Panel(args.handle, args.x, args.y))
            # fit the panel internally?
            # fitting should all happen at the same time
        elif args == 'pad':
            panel = gui.get(args.handle)  # throws ValueError
            panel.pad_left = args.x
            panel.pad_right = args.x
            panel.pad_top = args.y
            panel.pad_bottom = args.y
        elif args == 'fit':
            panel = gui.get(args.handle)
            panel.size = args.size
            panel.anchor = args.anchor
        elif args == 'ele':
            panel = gui.get(args.handle)
            panel.element_w = args.x
            panel.element_h = args.y

    # Fitting
    # First the panels within the canvas
    # TODO throw errors if dimensions are too big
    for panel in gui.panels:
        if panel.anchor == 'top':
            panel.w = gui.w - gui.pad_left - gui.pad_right
            panel.h = panel.size
            panel.x = gui.pad_left
            panel.y = gui.pad_top
            gui.pad_top += panel.h
        elif panel.anchor == 'bottom':
            panel.w = gui.w - gui.pad_left - gui.pad_right
            panel.h = panel.size
            panel.x = gui.pad_left
            panel.y = gui.h - gui.pad_bottom - panel.size
            gui.pad_bottom += panel.size
        elif panel.anchor == 'left':
            panel.w = panel.size
            panel.h = gui.h - gui.pad_top - gui.pad_bottom
            panel.x = gui.pad_left
            panel.y = gui.pad_top
            gui.pad_left += panel.size
        elif panel.anchor == 'right':
            panel.w = panel.size
            panel.h = gui.h - gui.pad_top - gui.pad_bottom
            panel.x = gui.w - gui.pad_right - panel.size
            panel.y = gui.pad_top
            gui.pad_right += panel.size
        elif panel.anchor == 'center':
            # placing a center panel will prevent any further panels
            # TODO integrate limited size, e.g. 80 by 80
            panel.w = gui.w - gui.pad_left - gui.pad_right
            panel.h = gui.h - gui.pad_top - gui.pad_bottom
            panel.x = gui.pad_left
            panel.y = gui.pad_top
            gui.pad_left = gui.w
            gui.pad_right = gui.w
            gui.pad_top = gui.h
            gui.pad_bottom = gui.h
        else:
            raise ValueError("Invalid anchor: '{}'!".format(anchor))
    # Then the elements within the panels
    return gui
