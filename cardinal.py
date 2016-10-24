
import malt
import numpy as np

# TODO: functions for text entry


MALT_SYNTAX = [
    "split s:direction, f:size",
]


class Interface:
    def __init__(self, layout_file, size):
        # next goal: find 20% of screen size
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
                    malt.log("Adding new split on {}.".format(line.direction))
                    malt.log("Taking {}% of screen size.".format(
                        round(line.size*100)))
                    self.add_split(line.direction.lower(), line.size)
                else:
                    malt.log("Unknown split direction: {}.".format(line.direction),
                        level="ERROR")
            else:
                malt.log("Unknown command in layout file: {}.".format(
                    line.head), level="ERROR")

    def add_split(self, d, percent_size):
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
        self.splits.append(absolute_vertices(x, y, w, h))

    def dump_splits(self):
        for v1, v2, v3, v4 in self.splits:
            malt.log("{}, {}, {}, {}".format(v1, v2, v3, v4))

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


class Split:
    pass


def absolute_vertices(x, y, w, h):
    """
    Transform x,y position, width, and height into a quad.
    Returns four x,y coordinate pairs.
    >>> absolute_vertices(0, 0, 100, 100)
    ((0, 0), (100, 0), (0, 100), (100, 100))
    """
    # REMEMBER: opengl origin point is BOTTOM LEFT, not top left.
    # We might have to do a tricksy transformation in here.
    # Although ultimately we should fix the wording to be consistent everywhere.
    v1 = (x, y)
    v2 = (x + w, y)
    v3 = (x, y + h)
    v4 = (x + w, y + h)
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
