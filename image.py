
import random
import numpy as np


def render_as_colors(gui):
    blank_tex = np.zeros((gui.h, gui.w, 4), dtype=np.uint8)
    for p in gui.panels:
        blank_tex[p.y:p.h+p.y, p.x:p.x+p.w, :] = color_block(p.h, p.w)
        for e in p.elements:
            blank_tex[e.y:e.h+e.y, e.x:e.x+e.w, :] = color_block(e.h, e.w)
    return blank_tex


def color_block(h, w):
    color = np.random.randint(256, size=(1, 1, 4))
    color[:, :, 3] = 255
    return np.repeat(np.repeat(color, h, axis=0), w, axis=1)


def blit(image, s, texture):
    (ih, iw, _) = image.shape
    if ih != s.h or iw != s.w:
        raise ValueError("Image is not the right size! ({}, {}) vs ({}, {})".format(
            iw, ih, s.w, s.h))
    # off by one?
    #texture[s.y:s.y+s.h, s.x:s.x+s.h, :] = image
    texture[s.y+2:s.y+2+s.h, s.x:s.x+s.h, :] = image
    return texture


def insert_all(image, panel, texture):
    for space in panel.spaces.values():
        texture = blit(image, space, texture)
    return texture
