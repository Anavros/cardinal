
import malt
import numpy as np

CONFIG_SYNTAX = [
    "div handle int(cols) int(rows)",
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
                return p
        raise ValueError("Panel not found.")


class Panel(object):
    def __init__(self, handle, cols, rows):
        self.handle = handle
        self.rows = rows
        self.cols = cols
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
        self.element_w = 0
        self.element_h = 0
        self.elements = []

    def at(self, x, y):
        for e in self.elements:
            if e.x <= x <= e.w+e.x and e.y <= y <= e.h+e.y:
                return e
        raise ValueError("Element not found.")


class Element(object):
    def __init__(self, handle):
        self.handle = handle
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0


def create(config_file, width, height):
    gui = Interface(width, height)
    for args in malt.load(config_file, CONFIG_SYNTAX):
        if args == 'div':
            gui.add(Panel(args.handle, args.cols, args.rows))
            # TODO: default arguments
            # actually that should be in the class spec
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
    for panel in gui.panels:
        total_w = panel.w - panel.pad_left - panel.pad_right
        total_h = panel.h - panel.pad_top - panel.pad_bottom
        element_w = panel.element_w
        element_h = panel.element_h
        if total_w < element_w*panel.cols or total_h < element_h*panel.rows:
            raise ValueError("({}, {}) can not fit ({}x{}, {}x{}) elements!".format(
                total_w, total_h, panel.cols, element_w, panel.rows, element_h))
        w_per = int(total_w/panel.cols)
        h_per = int(total_h/panel.rows)
        assert w_per > 0 and h_per > 0
        pad_w = int((w_per-element_w)/2)
        pad_h = int((h_per-element_h)/2)
        assert pad_w > 0 and pad_h > 0
        for c in range(panel.cols):
            for r in range(panel.rows):
                e = Element("{}[{}][{}]".format(panel.handle, c, r))
                e.x = c*w_per + pad_w + panel.x
                e.w = element_w
                e.y = r*h_per + pad_h + panel.y
                e.h = element_h
                panel.elements.append(e)
        #print(panel.handle, len(panel.elements))
    return gui
