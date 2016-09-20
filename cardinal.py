
import malt
import numpy as np

CONFIG_SYNTAX = [
    "div handle anchor[top|bottom|left|right|center] int(size)",
    "ele handle int(cols) int(rows) int(w) int(h) int(pad)",
    #"ele handle #cols #rows #w #h #pad",  # better format? shorter
]


#from cardinal import UI, Div
#for (verts, coord, index) in ui.renderables():
#label = ui.at(x, y)

ui = cardinal.Interface(W, H)
ui.insert('menu', 's', (1, 1))


class Interface:
    def __init__(self, px_width, px_height):
        self.w = px_width
        self.h = px_height

        self.panels = {}
        self.offset = { 'n':0, 's':0, 'e':0, 'w':0 }
        self.packed = False

    def get(self, handle):
        return self.panels[handle]

    def insert(self, panel):
        pass

    def renderables(self):
        pass

    def insert(self, p, anchor, size):
        if self.offset['center']:
            raise ValueError("The window is already full!")
        available_w = self.w - self.offset['left'] - self.offset['right']
        available_h = self.h - self.offset['top'] - self.offset['bottom']
        if (anchor in ['top', 'bottom'] and size > available_h) or \
        (anchor in ['left', 'right'] and size > available_w):
            raise ValueError("Panel {} is too large!.".format(p.handle))
        p.w = size if anchor in ['left', 'right'] else available_w
        p.h = size if anchor in ['top', 'bottom'] else available_h
        p.x = self.offset['left'] if anchor != 'right' else available_w - size
        p.y = self.offset['top'] if anchor != 'bottom' else available_h - size
        self.offset[anchor] += size
        self.required_w += p.w
        self.required_h += p.h
        self.panels.append(p)

    def at(self, x, y):
        """Return the panel located at (x, y) in logical pixels."""
        for p in self.panels:
            if p.x <= x <= p.w+p.x and p.y <= y <= p.h+p.y:
                return p, p.at(x, y)
        return None

    def find_by_nickname(self):
        pass


class Panel(object):
    def __init__(self, handle):
        self.handle = handle
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.elements = []
        self.spaces = {}
        self.element_w = 0
        self.element_h = 0

    def __getitem__(self, request):
        if type(request) is not tuple:
            raise TypeError("Panel elements must be accessed as panel[row, col].")
        return self.spaces[request]
        

    def make_grid(self, cols, rows, goal_w, goal_h, pad):
        # Position all sub-elements within the panel.
        internal_w = self.w - pad
        internal_h = self.h - pad
        if cols*goal_w > internal_w or rows*goal_h > internal_h:
            raise ValueError("Elements are too big! {}".format(self.handle))
        div_w = int(internal_w/cols)
        div_h = int(internal_h/rows)
        ext_w = internal_w - div_w*cols
        ext_h = internal_h - div_h*rows
        pad_w = div_w - goal_w if goal_w > 0 else 0
        pad_h = div_h - goal_h if goal_h > 0 else 0
        self.element_w = goal_w if goal_w > 0 else div_w
        self.element_h = goal_h if goal_h > 0 else div_h
        for c in range(cols):
            for r in range(rows):
                e = Element("{}[{}][{}]".format(self.handle, c, r))
                e.x = self.x + int(pad/2) + int(ext_w/2) + c*div_w + int(pad_w/2)
                e.w = goal_w if goal_w > 0 else div_w
                e.y = self.y + int(pad/2) + int(ext_h/2) + r*div_h + int(pad_h/2)
                e.h = goal_h if goal_h > 0 else div_h
                e.col = c
                e.row = r
                self.elements.append(e)
                self.spaces[c, r] = e

    def at(self, x, y):
        for e in self.spaces.values():
            if e.x <= x <= e.w+e.x and e.y <= y <= e.h+e.y:
                return e
        return None


class Element(object):
    def __init__(self, handle):
        self.handle = handle
        self.col = 0
        self.row = 0
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

    def coordinate(self):
        pass
