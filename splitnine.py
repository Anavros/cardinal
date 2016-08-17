#!/usr/bin/env python3

import numpy as np
from vispy import io


def stretch(path, new_x, new_y, d):
    image = io.imread(path)
    (ix, iy, iz) = image.shape
    scale_x = int(np.ceil(new_x/(ix - d*2)))
    scale_y = int(np.ceil(new_y/(iy - d*2)))
    scale_w = int(((ix-(2*d))*scale_x)+(2*d))
    scale_h = int(((iy-(2*d))*scale_y)+(2*d))

    new_image = np.full((scale_h, scale_w, iz), 256, dtype=image.dtype)
    new_image[  : d,  d:-d, :] = _scale(image[  : d,  d:-d, :], scale_x, 1) # top
    new_image[-d:  ,  d:-d, :] = _scale(image[-d:  ,  d:-d, :], scale_x, 1) # bot
    new_image[ d:-d,   : d, :] = _scale(image[ d:-d,   : d, :], 1, scale_y) # lft
    new_image[ d:-d, -d:  , :] = _scale(image[ d:-d, -d:  , :], 1, scale_y) # rht
    new_image[ d:-d,  d:-d, :] = _scale(image[ d:-d,  d:-d, :], scale_x, scale_y) # mid
    new_image[  : d,   : d, :] = image[  : d,   : d, :] # tlc
    new_image[  : d, -d:  , :] = image[  : d, -d:  , :] # trc
    new_image[-d:  ,   : d, :] = image[-d:  ,   : d, :] # blc
    new_image[-d:  , -d:  , :] = image[-d:  , -d:  , :] # brc

    new_image = _trim(new_image, new_x, new_y)
    return new_image
    #io.imsave(new_path, new_image)


def save(path, new_path, x, y, d):
    image = stretch(path, x, y, d)
    io.imsave(new_path, image)


def _scale(image, y, x):
    v = np.repeat(np.repeat(image, x, axis=0), y, axis=1)
    return v


def _trim(image, ny, nx):
    """Removes rows and columns from the middle of the image so that it's final
    dimensions match (x, y)."""
    (x, y, z) = image.shape
    #print(x, y, z)
    (dx, dy) = (x-nx, y-ny)
    #print(dx, dy)
    assert dx > 0 and dy > 0

    # inefficient! as if that matters at this point
    while True:
        image = np.delete(image, x/2, axis=0)
        x = image.shape[0]
        if x == nx:
            break
        elif x < nx:
            assert False, "Too far!"
        #print("trimmed the x")
    while True:
        image = np.delete(image, y/2, axis=1)
        y = image.shape[1]
        if y == ny:
            break
        elif y < ny:
            assert False, "Too far!"
        #print("trimmed the y")

    if image.shape[0] != nx or image.shape[1] != ny:
        print(image.shape, nx, ny)
        raise ValueError("Rounding problem!")
    return image
