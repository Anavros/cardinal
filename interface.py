
from vispy import io
import numpy as np
import splitnine
import malt


class Element(object):
    def __init__(self, handle, image, dimensions, padding):
        self.handle = handle
        self.image = image
        self.dimensions = dimensions
        self.padding = padding
        self.components = []


class Quad(object):
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    def unpack(self):
        return (self.x, self.y, self.w, self.h)
    def __repr__(self):
        return "Quad({}, {}, {}, {})".format(self.x, self.y, self.w, self.h)


def locate(x, y, elements):
    result = None
    for element in elements:
        d = element.dimensions
        if d.x < x < d.w+d.x and d.y < y < d.h+d.y:
            result = element.handle
            if element.components:
                deeper_result = locate(x, y, element.components)
                result = deeper_result if deeper_result else result
    return result


def build_gui(config_file, width, height):
    blank = np.zeros((height, width, 4), dtype=np.uint8)
    canvas = Element('canvas', blank, Quad(0, 0, width, height), Quad())
    for args in malt.load(config_file):
        if args.cmd != 'nest': raise ValueError() # TEMP

        parent = _find_parent(args.parent, [canvas])

        dimensions, parent.padding = _fit_element(
            args.anchor, args.size, parent.dimensions, parent.padding)

        dimensions.x += parent.dimensions.x
        dimensions.y += parent.dimensions.y

        print(parent.handle, args.handle, parent.padding)

        texture = splitnine.stretch(
            args.texture, dimensions.w, dimensions.h, args.cut)

        parent.components.append(
            Element(args.handle, texture, dimensions, Quad()))

    return [canvas]


def _find_parent(handle, elements):
    for e in elements:
        if e.handle == handle:
            return e
        elif e.components:
            return _find_parent(handle, e.components)
    raise IndexError("No parent container named {}.".format(handle))


def _fit_element(anchor, percent, parent, padding):
    scr = parent
    buf = padding
    ele = Quad()
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
    height = gui.canvas.dimensions.h
    width = gui.canvas.dimensions.w
    texture = np.full((height, width, 4), 255, dtype=np.uint8)
    for element in gui.elements:
        er = element.dimensions
        texture[er.y:er.h+er.y, er.x:er.w+er.x, :] = element.image
        for component in element.components:
            cr = component.dimensions
            cr.x += er.x
            cr.y += er.y
            texture[cr.y:cr.h+cr.y, cr.x:cr.w+cr.x, :] = component.image
    texture = np.flipud(texture) # XXX cause I can't figure why it's upside down
    return texture


#texture = np.full((ed.h, ed.w, 4), 255, dtype=np.uint8)
def xrender(elements, texture):
    for element in elements:
        # menu
        ed = element.dimensions
        texture[ed.y:ed.h+ed.y, ed.x:ed.w+ed.x, :] = element.image
        if element.components:
            # button1, 2
            texture = xrender(element.components, texture)
    return texture

# draw order
# canvas
#   menu
#     button1
#     button2
#   color_bar
#   other_bar
