
import random
import numpy as np


def render_as_colors(gui):
    blank_tex = np.zeros((gui.h, gui.w, 4), dtype=np.uint8)
    for panel in gui.panels:
        color = np.random.randint(256, size=(1, 1, 4))
        color[:, :, 3] = 255
        color_box = np.repeat(np.repeat(color, panel.h, axis=0), panel.w, axis=1)
        blank_tex[panel.y:panel.h+panel.y, panel.x:panel.x+panel.w, :] = color_box
        for e in panel.elements:
            ele_color = np.random.randint(256, size=(1, 1, 4))
            ele_color[:, :, 3] = 255
            ele_color_box = np.repeat(np.repeat(ele_color, e.h, axis=0), e.w, axis=1)
            blank_tex[e.y:e.h+e.y, e.x:e.x+e.w, :] = ele_color_box
    return blank_tex
