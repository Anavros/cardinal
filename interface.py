
from vispy import io
import numpy as np
import splitnine
import malt


class Element(object):
    def __init__(self, handle, image, dim, pad, mar):
        self.handle = handle
        self.image = image
        self.dim = dim
        self.pad = pad
        self.mar = mar
        self.components = []


class Quad(object):
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    def unpack(self):
        return (self.x, self.y, self.w, self.h)
    def add(self, n):
        return Quad(self.x+n, self.y+n, self.w+n, self.h+n)
    def __repr__(self):
        return "Quad({}, {}, {}, {})".format(self.x, self.y, self.w, self.h)


def locate(x, y, elements):
    result = None
    for element in elements:
        d = element.dim
        if d.x < x < d.w+d.x and d.y < y < d.h+d.y:
            result = element.handle
            if element.components:
                deeper_result = locate(x, y, element.components)
                result = deeper_result if deeper_result else result
    return result


def build_gui(config_file, width, height):
    blank = np.zeros((height, width, 4), dtype=np.uint8)
    canvas = Element('canvas', blank, Quad(0, 0, width, height), Quad().add(10), Quad())
    for args in malt.load(config_file):
        if args.cmd != 'nest': raise ValueError() # TEMP

        parent = _find_parent(args.parent, [canvas])
        child = Element(
            args.handle,
            image=None,
            dim=Quad(),
            pad=Quad().add(args.pad),
            mar=Quad().add(args.mar)
        )
        child, parent = _fit(child, parent, args.anchor, args.size)
        child.image = splitnine.stretch(args.texture, child.dim.w, child.dim.h, args.cut)
        parent.components.append(child)

    return [canvas]


def _find_parent(handle, elements):
    for e in elements:
        if e.handle == handle:
            return e
        elif e.components:
            return _find_parent(handle, e.components)
    raise IndexError("No parent container named {}.".format(handle))


def _fit(child, parent, anchor, size):
    if anchor == 'top':
        child.dim.w = parent.dim.w - parent.pad.w - parent.pad.x
        child.dim.h = int(parent.dim.h*size)
        child.dim.x = parent.dim.x + parent.pad.x
        child.dim.y = parent.dim.y + parent.pad.y
        parent.pad.y = parent.pad.y + child.dim.h
    elif anchor == 'bottom':
        child.dim.w = parent.dim.w - parent.pad.w - parent.pad.x
        child.dim.h = int(parent.dim.h*size) - parent.pad.h
        child.dim.x = parent.dim.x + parent.pad.x
        child.dim.y = parent.dim.y + parent.dim.h - child.dim.h
        parent.pad.h = parent.pad.h + child.dim.h
    elif anchor == 'left':
        child.dim.w = int(parent.dim.w*size)
        child.dim.h = parent.dim.h - parent.pad.h - parent.pad.y
        child.dim.x = parent.dim.x + parent.pad.x
        child.dim.y = parent.dim.y + parent.pad.y
        parent.pad.x = parent.pad.x + child.dim.w
    elif anchor == 'right':
        child.dim.w = int(parent.dim.w*size) - parent.pad.w
        child.dim.h = parent.dim.h - parent.pad.h - parent.pad.y
        child.dim.x = parent.dim.x + parent.dim.w - child.dim.w
        child.dim.y = parent.dim.y + parent.pad.y
        parent.pad.w = parent.pad.w + child.dim.w
    else:
        raise ValueError("Invalid anchor! This shouldn't happen!")
    return child, parent


def xrender(elements, texture):
    for element in elements:
        # menu
        ed = element.dim
        try:
            texture[ed.y:ed.h+ed.y, ed.x:ed.w+ed.x, :] = element.image
        except ValueError:
            #malt.serve(element)
            print("image is", element.image.shape)
            print("and should be", element.dim)
            raise
        if element.components:
            # button1, 2
            texture = xrender(element.components, texture)
    return texture
