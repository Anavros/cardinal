#!/usr/bin/env python3

import numpy as np
from vispy import io


def stretch(path, new_path, x, y, d):
    image = io.imread(path)
    #print(image.dtype, image.shape)
    #input()
    # image = 16, 16, 4
    # newim = ((16-2d)*4)+2d == 28, 28, 4

    new_image = np.full((28, 28, 4), 256, dtype=np.uint8)
    ##print(new_image.dtype, new_image.shape)
    #input()
    new_image[  : d,  d:-d, :] = _scale(image[  : d,  d:-d, :], 4, 1) # top
    new_image[-d:  ,  d:-d, :] = _scale(image[-d:  ,  d:-d, :], 4, 1) # bot
    new_image[ d:-d,   : d, :] = _scale(image[ d:-d,   : d, :], 1, 4) # lft
    new_image[ d:-d, -d:  , :] = _scale(image[ d:-d, -d:  , :], 1, 4) # rht
    new_image[ d:-d,  d:-d, :] = _scale(image[ d:-d,  d:-d, :], 4, 4) # mid
    new_image[  : d,   : d, :] = image[  : d,   : d, :] # tlc
    new_image[  : d, -d:  , :] = image[  : d, -d:  , :] # trc
    new_image[-d:  ,   : d, :] = image[-d:  ,   : d, :] # blc
    new_image[-d:  , -d:  , :] = image[-d:  , -d:  , :] # brc

    io.imsave(new_path, new_image)


def _scale(image, y, x):
    return np.repeat(np.repeat(image, x, axis=0), y, axis=1)


if __name__ == '__main__':
    stretch('nine.png', 'nine_128.png', 128, 128, 6)
