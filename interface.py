
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


class Panel(object):
    def __init__(self, handle):
        self.handle = handle
        self.spacing = None
        self.image_path = None


# two ways to render element:
# load texture from ele.image_path and place at ele.x, ele.y
# create image programmatically, size with ele.wh and place with ele.xy

# or should we store textures within elements?
# doesn't work very well if it's a dynamic texture like a minimap or text or something
# so no
# or maybe it does work ok
# you'd have to pass them in anyway, and if they're already in the object
# it makes it easier to render everything in one go

# and then what about multiple textures for one element
# like a button with normal, clicked, and hovered over textures
# maybe each object can have a state?
# just arbitrary, specified in the config file
# and then depending on the state, the programmer could pass in different textures?
# but the config file stores the textures
# so the programmer shouldn't have to pass them in
# maybe all of the textures can be included in a dict or something

# so each query for an element would return its handle and state
# and there would be a rendering function that automatically handled all of that
# and probably a function to set a texture on an object

# well, all of this rendering and passing around should really be done by the gpu
# the gui really should only be managing the placement of things
# just a means to turn coordinates into handles


class Button(object):
    def __init__(self, handle):
        self.handle = handle


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


class UserInterface(object):
    def __init__(self):
        self.panels = []
        self.groups = []
        self.buttons = []


def create(config_file, width, height):
    # spawn a new UserInterface()
    # load elements from config file into appropriate lists
    # space panels within interface
    # for each panel space elements within panel
    # return interface
    pass

# should textures and rendering be done in a separate module?
# only leave spacing for this one?


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
    canvas = Element(
        'canvas',
        blank,
        Quad(0, 0, width, height),
        Quad(),
        Quad()
    )

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
    c = child
    p = parent
    if anchor == 'top':
        c.dim.w = p.dim.w - p.pad.w - p.pad.x
        c.dim.h = int(p.dim.h*size)
        c.dim.x = p.dim.x + p.pad.x
        c.dim.y = p.dim.y + p.pad.y
        p.pad.y += c.dim.h
    elif anchor == 'bottom':
        c.dim.w = p.dim.w - p.pad.w - p.pad.x
        c.dim.h = int(p.dim.h*size) - p.pad.h
        c.dim.x = p.dim.x + p.pad.x
        c.dim.y = p.dim.y + p.dim.h - c.dim.h - p.pad.h
        p.pad.h += c.dim.h
    elif anchor == 'left':
        c.dim.w = int(p.dim.w*size)
        c.dim.h = p.dim.h - p.pad.h - p.pad.y
        c.dim.x = p.dim.x + p.pad.x
        c.dim.y = p.dim.y + p.pad.y
        p.pad.x += c.dim.w
    elif anchor == 'right':
        c.dim.w = int(p.dim.w*size) - p.pad.w
        c.dim.h = p.dim.h - p.pad.h - p.pad.y
        c.dim.x = p.dim.x + p.dim.w - c.dim.w - p.pad.w
        c.dim.y = p.dim.y + p.pad.y
        p.pad.w += c.dim.w
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
