
from vispy import io
import numpy as np
import splitnine
import malt


def locate_div(x, y, gui):
    for element in gui.elements:
        e = element.rect
        if e.x < x < e.w+e.x and e.y < y < e.h+e.y:
            return element.handle


class GUI(object):
    def __init__(self, elements, scr, buf):
        self.elements = elements
        self.scr = scr
        self.buf = buf


class Element(object):
    def __init__(self, handle, rect, texture):
        self.handle = handle
        self.rect = rect
        self.texture = texture


class Button(object):
    pass


class Quad(object):
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


def build_gui(config_file, screen_w, screen_h):
    elements = []
    buf = Quad()
    scr = Quad(0, 0, screen_w, screen_h)
    for (command, args) in malt.load(config_file):
        if command == 'div':
            ele, buf = _build_div(args, scr, buf)
            elements.append(ele)
        elif command == 'button':
            pass
    return GUI(elements, scr, buf)


def _build_div(args, scr, buf):

    handle = args['handle']
    anchor = args['anchor']
    tex_path = args['texture']
    size = args['size']

    ele, buf = _fit_element(anchor, size, scr, buf)
    texture = splitnine.stretch(tex_path, ele.w, ele.h, 12) # TODO

    return Element(handle, ele, texture), buf


def _build_button():
    pass


def _fit_element(anchor, percent, screen_quad, buffer_quad):
    scr = screen_quad
    buf = buffer_quad
    ele = Quad()
    #(xb, yb, wb, hb) = buffers
    if anchor == 'top':
        ele.w = scr.w - buf.w - buf.x
        ele.h = int(scr.h*percent)
        ele.x = buf.x
        ele.y = buf.y
        buf.y = buf.y + ele.h
    elif anchor == 'bottom':
        ele.w = scr.w - buf.w - buf.x
        ele.h = int(scr.h*percent) - buf.h
        ele.x = buf.x
        ele.y = scr.h - ele.h
        buf.h = buf.h + ele.h
    elif anchor == 'left':
        ele.w = int(scr.w*percent)
        ele.h = scr.h - buf.h - buf.y
        ele.x = buf.x
        ele.y = buf.y
        buf.x = buf.x + ele.w
    elif anchor == 'right':
        ele.w = int(scr.w*percent) - buf.w
        ele.h = scr.h - buf.h - buf.y
        ele.x = scr.w - ele.w
        ele.y = buf.y
        buf.w = buf.w + ele.w
    else:
        raise ValueError("Invalid anchor! This shouldn't happen!")
    return ele, buf


def render(gui):
    texture = np.full((gui.scr.h, gui.scr.w, 4), 255, dtype=np.uint8)
    for e in gui.elements:
        r = e.rect
        texture[r.y:r.h+r.y, r.x:r.w+r.x, :] = e.texture
    texture = np.flipud(texture) # XXX cause I can't figure why it's upside down
    return texture
