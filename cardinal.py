
import malt
import numpy as np


MALT_SYNTAX = [
    "split s:direction, f:size",
]


# cardinal.Interface()
# cardinal.Split()
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
        y = self.offsets['n'] if d != 's' else available_h - size
        self.offsets[d] += size
        # Second step: find absolute vertices.
        v1 = (x, y)
        v2 = (x + w, y)
        v3 = (x, y + h)
        v4 = (x + w, y + h)
        self.splits.append((v1, v2, v3, v4))

    def dump_splits(self):
        for v1, v2, v3, v4 in self.splits:
            malt.log("{}, {}, {}, {}".format(v1, v2, v3, v4))

    def render(self):
        n = len(self.splits)*4
        vertices = np.zeros(shape=(n, 2), dtype=np.float32)
        colors = np.zeros(shape=(n, 3), dtype=np.float32)
        for i, split in enumerate(self.splits):
            # An array of three random floats in the range [0.0,1.0].
            split_color = np.random.random(size=(3))
            for j, vertex in enumerate(split):
                vertices[i+j] = screen_space((self.w, self.h), vertex)
                colors[i+j] = split_color
        return vertices, colors

#    def render_vertices(self):
#        vertices = np.zeros(shape=(len(self.splits)*4, 2), dtype=np.float32)
#        for i, split in enumerate(self.splits):
#            for j, vertex in enumerate(split):
#                vertices[i+j] = screen_space((self.w, self.h), vertex)
#        return vertices
#
#    def render_colors(self):
#        colors = np.zeros(shape=(n*4, 3), dtype=np.uint8)
#        # There's probably a more idiomatic way of doing this.
#        for i in range(n):
#            colors[i] = np.random.randint(3)
#        return colors


class Split:
    pass


def screen_space(screen_size, vertex):
    """
    Normalize a pixel-wise split into [-1, +1] screen space.
    >>> screen_space((100, 100), (50, 50))
    (0.0, 0.0)
    >>> screen_space((100, 100), (75, 25))
    (0.5, -0.5)
    >>> screen_space((100, 100), (0, 0))
    (-1.0, -1.0)
    >>> screen_space((100, 100), (100, 100))
    (1.0, 1.0)
    """
    x, y = vertex
    w, h = screen_size
    a = 2*x/w - 1
    b = 2*y/h - 1
    return (a, b)
