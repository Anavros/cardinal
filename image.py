
import random
import numpy as np
from vispy import io

import splitnine


def render_as_colors(gui):
    print("rendering colors")
    blank_tex = np.zeros((gui.h, gui.w, 4), dtype=np.uint8)
    for p in gui.panels:
        blank_tex[p.y:p.h+p.y, p.x:p.x+p.w, :] = color_block(p.h, p.w)
        for e in p.elements:
            blank_tex[e.y:e.h+e.y, e.x:e.x+e.w, :] = color_block(e.h, e.w)
    return blank_tex


def gpu_render_as_colors(gui):
    renderables = []
    for p in gui.panels:
        rand_color = np.random.randint(255, size=(3), dtype=np.uint8)
        p_verts = np.array([
            #(p.x, p.y+p.h), (p.x+p.w, p.y+p.h),
            #(p.x, p.y    ), (p.x+p.w, p.y    ),
            (-1.0,  0.0), (+1.0,  0.0),
            (-1.0, -1.0), (+1.0, -1.0),
        ], dtype=np.float32)
        p_color = np.array([
            rand_color, rand_color,
            rand_color, rand_color,
        ], dtype=np.float32)
        p_index = np.array([
            0, 1, 2, 3
        ], dtype=np.uint32)
        renderables.append((p_verts, p_color, p_index))
    return renderables
        


def imperfect_blit(image, s, anchor, slate):
    # assume anchor is center
    ih, iw, iz = image.shape
    x = s.x + int(s.w/2) - int(iw/2)
    y = s.y + int(s.h/2) - int(ih/2)
    slate[y:y+ih, x:x+iw, :3] = image
    return slate


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


def fill(image_path, panel, slate, stretch=None):
    if stretch:
        image = splitnine.stretch(image_path, panel.w, panel.h, stretch)
    else:
        image = io.imread(image_path)
    return blit(image, panel, slate)


def fill_all(image_path, panel, slate, stretch=None):
    (w, h) = panel.element_w, panel.element_h
    if stretch:
        image = splitnine.stretch(image_path, w, h, stretch)
    else:
        image = io.imread(image_path)
    for element in panel.spaces.values():
        slate = blit(image, element, slate)
    return slate


def matching_sizes(image, target_w, target_h):
    (image_h, image_w, _) = image.shape
    return (target_w == image_w or target_h == image_h)
