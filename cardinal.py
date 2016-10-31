
import malt
log = malt.log
import numpy as np
import geometry

# TODO: functions for text entry


MALT_SYNTAX = [
    "split s:name, s:direction, f:size",
]


class Interface:
    def __init__(self, layout_file, size):
        self.w, self.h = size
        self.splits = []
        self.offsets = {
            'n': 0,
            's': 0,
            'e': 0,
            'w': 0,
        }
        self.load_layout_file(layout_file)

    def load_layout_file(self, layout_file):
        """
        Configures this interface to the layout specified in the given file.
        Used internally. Filename is passed from the constructor.
        """
        for line in malt.load(layout_file, MALT_SYNTAX):
            if line.head == 'split':
                if line.direction.lower() in "nsew":
                    log("Adding new split on {}.".format(line.direction),
                        level='LAYOUT')
                    log("Taking {}% of screen size.".format(
                        round(line.size*100)), level='LAYOUT')
                    self.add_split(line.name, line.direction.lower(), line.size)
                else:
                    log("Unknown direction: {}.".format(line.direction),
                        level="ERROR")
            else:
                log("Unknown command in layout file: {}.".format(
                    line.head), level="ERROR")

    def add_split(self, name, d, percent_size):
        """
        Adds a split to the interface. Used internally. TODO: doctests?
        Should probably be split up into several smaller functions.
        """
        # Preparing temporary variables.
        assert percent_size <= 1.0
        if d in ['n', 's']:
            axis = 'vertical'
            size = self.h * percent_size
        else:
            axis = 'horizontal'
            size = self.w * percent_size
        # First step: find x,y position and w,h.
        available_w = self.w - self.offsets['w'] - self.offsets['e']
        available_h = self.h - self.offsets['n'] - self.offsets['s']
        if any([
            d in ['n', 's'] and size > available_h,
            d in ['w', 'e'] and size > available_w
        ]): raise ValueError("Split is too large!")
        w = size if d in ['w', 'e'] else available_w
        h = size if d in ['n', 's'] else available_h
        x = self.offsets['w'] if d != 'e' else available_w - size
        #y = self.offsets['n'] if d != 's' else available_h - size
        y = self.offsets['s'] if d != 'n' else self.h - self.offsets['n'] - size
        self.offsets[d] += size
        split = Split(name, d, percent_size, absolute_vertices(x, y, w, h))
        self.splits.append(split)

    def dump_splits(self):
        for v1, v2, v3, v4 in self.splits:
            log("{}, {}, {}, {}".format(v1, v2, v3, v4))

    def render(self):
        n = len(self.splits)*4
        verts = np.zeros(shape=(n, 2), dtype=np.float32)
        color = np.zeros(shape=(n, 3), dtype=np.float32)
        for i, split in enumerate(self.splits):
            q = i*4  # step in fours
            # An array of three random floats in the range [0.0,1.0].
            color[q:q+4] = np.random.random(size=(3))
            for j, vertex in enumerate(split):
                verts[q+j] = screen_space((self.w, self.h), vertex)
        return verts, color

    def indices(self):
        # for every four vertices: 1, 2, 3, 4
        # we need six indices: 1, 2, 3,  2, 3, 4
        n = len(self.splits)
        index = np.zeros((n, 6), dtype=np.uint8)
        for i in range(n):
            q = i*4
            index[i] = [q, q+1, q+2, q+1, q+2, q+3]
        return index

    def at(self, pos):
        for split in self.splits:
            if geometry.inside(pos, split.vertices):
                return split
        # If not found.
        return None



class Split:
    def __init__(self, name, d, per, verts):
        self.name = name
        self.direction = d
        self.percent = per
        self.vertices = verts

    def __iter__(self):
        for v in self.vertices:
            yield v

    def __repr__(self):
        return "Split(name={}, verts={})".format(self.name, self.vertices)


def absolute_vertices(x, y, w, h):
    """
    Transform x,y position, width, and height into a quad.
    Returns four x,y coordinate pairs.
    >>> absolute_vertices(0, 0, 100, 100)
    ((0, 100), (100, 100), (0, 0), (100, 0))

    The order goes: top left, top right, bottom left, bottom right.
    """
    # REMEMBER: opengl origin point is BOTTOM LEFT, not top left.
    # We might have to do a tricksy transformation in here.
    # Although ultimately we should fix the wording to be consistent everywhere.
    v1 = (x, y + h)
    v2 = (x + w, y + h)
    v3 = (x, y)
    v4 = (x + w, y)
    return (v1, v2, v3, v4)


def screen_space(screen_size, vertex):
    """
    Normalize a pixel-wise split into [-1, +1] screen space.
    >>> size = (100, 100)
    >>> screen_space(size, (50, 50))
    (0.0, 0.0)
    >>> screen_space(size, (75, 25))
    (0.5, -0.5)
    >>> screen_space(size, (0, 0))
    (-1.0, -1.0)
    >>> screen_space(size, (100, 100))
    (1.0, 1.0)
    """
    x, y = vertex
    w, h = screen_size
    a = 2*x/w - 1
    b = 2*y/h - 1
    return (a, b)
