
from vispy import io
import numpy as np
import splitnine
import malt


def on_mouse_press(event):
    # when clicked, detect where the click occurred and reference against a table
    # of elements. if the click matches an element, signal that element.
    # so we'll need a table of elements and their locations.
    # if we have a table, we could use that for rendering too.
    # plus then you could edit it externally in a text file or something.
    # might need to be an ordered structure
    print('click')
    gui_table = {
        "menu": (0, 0, 230, 230),
        "other": (200, 300, 100, 200)
    }

    if event.type == 'mouse_press':
        (x, y) = event.pos
        pos_to_div(x, y, gui_table)


def pos_to_div(ex, ey, gui_table):
    for handle, corners in gui_table.items():
        (x, y, w, h) = corners
        if x < ex < w+x and y < ey < h+y:
            print("you clicked on {}!".format(handle))


class GUI(object):
    def __init__(self, elements, rect):
        self.elements = elements
        self.texture = None
        self.rect = rect
        (self.x, self.y, self.w, self.h) = rect


class Element(object):
    def __init__(self, handle, corners, texture):
        self.handle = handle
        self.rect = rect
        (self.x, self.y, self.w, self.h) = rect
        self.texture = texture


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


def build_gui(config_file, screen_w, screen_h):
    elements = []
    for (command, args) in malt.load(config_file).items():
        # assume every command is div right now
        handle = args['id']
        (ex, ey, ew, eh) = _corners(args['anchor'], args['size'], screen_w, screen_h)
        tex_path = args['texture']
        e_tex = splitnine.stretch(tex_path, ew, eh, 12) # TODO
        elements.append(Element(handle, (ex, ey, ew, eh), e_tex))
    return GUI(elements, (0, 0, screen_w, screen_h))


def _corners(anchor, percent, screen_w, screen_h):
    if anchor == 'top':
        ew = screen_w
        eh = int(screen_h*percent)
        ex = 0
        ey = 0
    elif anchor == 'bottom':
        ew = screen_w
        eh = int(screen_h*percent)
        ex = 0
        ey = screen_h - eh
    elif anchor == 'left':
        ew = int(screen_w*percent)
        eh = screen_h
        ex = 0
        ey = 0
    elif anchor == 'right':
        ew = int(screen_w*percent)
        eh = screen_h
        ex = screen_w - ew
        ey = 0
    else:
        raise ValueError("Invalid anchor! This shouldn't happen!")
    return (ex, ey, ew, eh)


def render(gui):
    texture = np.full((gui.y, gui.x, 4), 255, dtype=np.uint8)
    for e in gui.elements:
        texture[e.x:e.w, e.y:e.h, :] = e.texture
    texture = np.rot90(texture, k=2) # XXX cause I can't figure why it's upside down
    return texture

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
