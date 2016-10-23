
import malt
import numpy as np


MALT_SYNTAX = [
    "butt",
]


# cardinal.Interface()
# cardinal.Split()
class Interface:
    def __init__(self, layout_file, size):
        for line in malt.load(layout_file, MALT_SYNTAX):
            pass

    def render_vertices(self):
        return np.zeros((1, 2), dtype=np.float32)


class Split:
    pass
