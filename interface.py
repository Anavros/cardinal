
from vispy import io
import numpy as np
import splitnine
import malt


def locate_div(x, y, gui):
    for e in gui.elements:
        if e.x < x < e.w+e.x and e.y < y < e.h+e.y:
            print("Element '{}' has been triggered!".format(e.handle))


class GUI(object):
    def __init__(self, elements, rect):
        self.elements = elements
        self.texture = None
        self.rect = rect
        (self.x, self.y, self.w, self.h) = rect


class Element(object):
    def __init__(self, handle, rect, texture):
        self.handle = handle
        self.rect = rect
        (self.x, self.y, self.w, self.h) = rect
        self.texture = texture


def build_gui(config_file, screen_w, screen_h):
    elements = []
    for (command, args) in malt.load(config_file):
        # assume every command is div right now
        handle = args['handle']
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
    texture = np.full((gui.h, gui.w, 4), 255, dtype=np.uint8)
    for e in gui.elements:
        print(gui.x, gui.y, gui.w, gui.h)
        print(e.x, e.y, e.w, e.h)
        texture[e.y:e.h+e.y, e.x:e.w+e.x, :] = e.texture
    texture = np.flipud(texture) # XXX cause I can't figure why it's upside down
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
