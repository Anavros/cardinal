
import malt
import numpy as np

CONFIG_SYNTAX = [
    "div handle int(cols) int(rows)",
    "fit handle anchor[top|bottom|left|right|center] int(size)",
    "ele handle int(x) int(y)",
    "pad handle int(x) int(y)",
]


def create(config_file, width, height):
    gui = Interface(width, height)
    for args in malt.load(config_file, CONFIG_SYNTAX):
        if args == 'div':
            gui.add(Panel(args.handle, args.cols, args.rows))
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

    # TODO throw errors if dimensions are too big
    return space(gui)


def space(gui):
    offset = { 'top': 0, 'bottom': 0, 'left': 0, 'right': 0 }
    for p in gui.panels:
        # Position the panel within the screen.
        available_w = gui.w - offset['left'] - offset['right']
        available_h = gui.h - offset['top'] - offset['bottom']
        p.w = p.size if p.anchor in ['left', 'right'] else available_w
        p.h = p.size if p.anchor in ['top', 'bottom'] else available_h
        p.x = offset['left'] if p.anchor != 'right' else available_w - p.size
        p.y = offset['top'] if p.anchor != 'bottom' else available_h - p.size
        offset[p.anchor] += p.size

        # Position all sub-elements within the panel.
        total_w = p.w - p.pad_left - p.pad_right
        total_h = p.h - p.pad_top - p.pad_bottom
        (c_space, c_pad) = _fit(total_w, p.cols, p.element_w)
        (r_space, r_pad) = _fit(total_h, p.rows, p.element_h)
        for c in range(p.cols):
            for r in range(p.rows):
                e = Element("{}[{}][{}]".format(p.handle, c, r))
                e.x = c*c_space + c_pad + p.x
                e.w = p.element_w
                e.y = r*r_space + r_pad + p.y
                e.h = p.element_h
                p.elements.append(e)
    return gui



def _fit(total_space, num_items, item_size):
    space_per_item = int(total_space/num_items)
    pad = int((space_per_item - item_size)/2)
    return (space_per_item, pad)


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
