
import numpy as np


def on_click(event):
    # when clicked, detect where the click occurred and reference against a table
    # of elements. if the click matches an element, signal that element.
    # so we'll need a table of elements and their locations.
    # if we have a table, we could use that for rendering too.
    # plus then you could edit it externally in a text file or something.
    pass


def fit(anchor, x, y):
    """Calculates stretch and slip to make a quad fill a certain amount of space."""

    # fit(left, 1, 0.5): scale.x = 1, scale.y=0.5, slip.x=0, slip.y=0
    scale = (x, y)
    if anchor == 'top':
        slip = (0, 1-y)
    elif anchor == 'bottom':
        slip = (0, -1+y)
    elif anchor == 'left':
        slip = (-1+x, 0)
    elif anchor == 'right':
        slip = (1-x, 0)
    else:
        raise ValueError

    return scale, slip


def split_nine(image, cut_depth):
    # 
    #texture = io.imread('nine.png')
    pass


def stretch_nine(pieces, x, y):
    return np.array([np.array([np.arange(256)]*256)]*4)


#bird_selector_bar = {}

r"""
There are two kinds of gui graphics: things that stretch and things that don't.
Some graphics need to be pixel-perfect to be sharp. So we have to have some sort of
feature that allows very specific pixel dimensions, and not just percentages of the
screen.

...Maybe we shouldn't even worry about this stuff yet. We could just make the screen
a static size and forget about it all until later. It's really kind of an advanced
feature. It's not that important.
"""
