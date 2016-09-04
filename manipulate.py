
import numpy as np


def crop(): pass
def stretch(): pass
def scale(): pass


def coordinate(layout):
    """
    Calculate opengl vertices, texcoords, and indices for every element in a layout.

    For each element in the layout, return a (verts, coord, index) triplet.
    """
    for panel in layout:
        for element in panel:
            pass
    return verts, coord, index


def gui_nine_split(scr, tex, cut):
    # example: screen_size = (100, 100), tex_size=(32, 32), cut_depth=12
    # 0.88 = 1-(12/100)
    # 0.375 = 12/32
    # 0.625 = 1-(12/32)
    v = 1-(cut/scr)
    t1 = cut/tex
    t2 = 1-t1
    verts = np.array([
        (-1.0, +1.0), (-v, +1.0 ), (+v, +1.0 ), (+1.0, +1.0 ),
        (-1.0, +v), (-v, +v), (+v, +v), (+1.0, +v),
        (-1.0, -v), (-v, -v), (+v, -v), (+1.0, -v),
        (-1.0, -1.0), (-v, -1.0 ), (+v, -1.0 ), (+1.0, -1.0 ),
    ], dtype=np.float32)
    coord = np.array([
        (0, 1    ), (t1, 1    ), (t2, 1    ), (1, 1    ),
        (0, t2), (t1, t2), (t2, t2), (1, t2),
        (0, t1), (t1, t1), (t2, t1), (1, t1),
        (0, 0    ), (t1, 0    ), (t2, 0    ), (1, 0    ),
    ], dtype=np.float32)
    index = np.array([
        0, 4, 1, 5, 2, 6, 3, 7, 6, 11, 10, 15, 14, 10, 13, 9, 12, 8, 9, 4, 5, 6, 9, 10
    ], dtype=np.uint32)
    return verts, coord, index
