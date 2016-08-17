
from vispy import io
import numpy as np
import splitnine
import malt


def locate_div(x, y, gui):
    for e in gui.elements:
        if e.x < x < e.w+e.x and e.y < y < e.h+e.y:
            return e.handle


class GUI(object):
    def __init__(self, elements, rect):
        self.elements = elements
        self.texture = None
        self.rect = rect
        (self.x, self.y, self.w, self.h) = rect
        self.buffers = (0, 0, 0, 0)


class Element(object):
    def __init__(self, handle, rect, buff, texture):
        self.handle = handle
        self.rect = rect
        self.buff = buff
        (self.x, self.y, self.w, self.h) = rect
        (self.xb, self.yb, self.wb, self.hb) = buff
        self.texture = texture


# TODO: cleanup
def build_gui(config_file, screen_w, screen_h):
    elements = []
    (xb, yb, wb, hb) = (0, 0, 0, 0)
    for (command, args) in malt.load(config_file):
        # assume every command is div right now
        handle = args['handle']
        (ex, ey, ew, eh) = _corners(
            args['anchor'], args['size'], screen_w, screen_h, (xb, yb, wb, hb))
        tex_path = args['texture']
        (tex_w, tex_h) = (ew, eh)
        e_tex = splitnine.stretch(tex_path, tex_w, tex_h, 12) # TODO
        elements.append(Element(handle, (ex, ey, ew, eh), (xb, yb, wb, hb), e_tex))
        (xb, yb, wb, hb) = _buffers(args['anchor'], (ex,ey,ew,eh), (xb,yb,wb,hb))
    return GUI(elements, (0, 0, screen_w, screen_h))


def _buffers(anchor, corners, buffers):
    (ex, ey, ew, eh) = corners
    (xb, yb, wb, hb) = buffers
    if anchor == 'top':
        return (xb, yb+eh, wb, hb)
    elif anchor == 'bottom':
        return (xb, yb, wb, hb+eh)
    elif anchor == 'left':
        return (xb+ew, yb, wb, hb)
    elif anchor == 'right':
        return (xb, yb, wb+ew, hb)


def _corners(anchor, percent, screen_w, screen_h, buffers=(0, 0, 0, 0)):
    (xb, yb, wb, hb) = buffers
    if anchor == 'top':
        ew = screen_w - wb - xb
        eh = int(screen_h*percent)
        ex = 0 + xb
        ey = 0 + yb
    elif anchor == 'bottom':
        ew = screen_w - wb - xb
        eh = int(screen_h*percent) - hb
        ex = 0 + xb
        ey = screen_h - eh
    elif anchor == 'left':
        ew = int(screen_w*percent)
        eh = screen_h - hb - yb
        ex = 0 + xb
        ey = 0 + yb
    elif anchor == 'right':
        ew = int(screen_w*percent) - wb
        eh = screen_h - hb - yb
        ex = screen_w - ew
        ey = 0 + yb
    else:
        raise ValueError("Invalid anchor! This shouldn't happen!")
    return (ex, ey, ew, eh)


def render(gui):
    texture = np.full((gui.h, gui.w, 4), 255, dtype=np.uint8)
    for e in gui.elements:
        texture[e.y:e.h+e.y, e.x:e.w+e.x, :] = e.texture
    texture = np.flipud(texture) # XXX cause I can't figure why it's upside down
    return texture
