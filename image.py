
import random
import numpy as np


def render_as_colors(gui):
    print("rendering colors")
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
    texture[s.y:s.y+s.h, s.x:s.x+s.w, :] = image
    return texture


def insert_all(image, panel, texture):
    for space in panel.spaces.values():
        texture = blit(image, space, texture)
    return texture


def composite(images):
    (ih, iw, iz) = images[0].shape
    slate = np.zeros((ih, iw, iz), dtype=images[0].dtype)
    for image in images:
        assert image.shape == images[0].shape
        slate_color = slate[:, :, :3].astype(np.float32) / 255.0
        slate_alpha = slate[:, :, 3].astype(np.float32) / 255.0
        image_color = image[:, :, :3].astype(np.float32) / 255.0
        image_alpha = image[:, :, 3].astype(np.float32) / 255.0

        combo_alpha = image_alpha + slate_alpha*(1.0-image_alpha)
        combo_color = (image_color*image_alpha[:,:,None] + 
            slate_color*slate_alpha[:,:,None] *
            (1.0-image_alpha[:,:,None])) / combo_alpha[:,:,None]

        combo_alpha = combo_alpha*255
        combo_color = combo_color*255
        slate[:, :, 3] = combo_alpha.astype(np.uint8)
        slate[:, :, :3] = combo_color.astype(np.uint8)
    return slate
