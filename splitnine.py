#!/usr/bin/env python3

import numpy as np
from vispy import io


def stretch(path, new_path, x, y, d):
    image = io.imread(path)

    # split the image into nine parts
    pieces = {
        "top": image[:d, d:-d, :],
        "bot": image[-d:, d:-d, :],
        "lft": image[d:-d, :d, :],
        "rht": image[d:-d, -d:, :],
        "mid": image[d:-d, d:-d, :],
        "tlc": image[:d, :d, :],
        "trc": image[:d, -d:, :],
        "blc": image[-d:, :d, :],
        "brc": image[-d:, -d:, :],
    }
    for k, v in pieces.items():
        v = np.repeat(np.repeat(v, 4, axis=0), 4, axis=1)
        io.imsave('pieces/{}.png'.format(k), v)

    new_image = np.repeat(np.repeat(image, 4, axis=0), 4, axis=1)
    io.imsave(new_path, new_image)


if __name__ == '__main__':
    stretch('nine.png', 'nine_128.png', 128, 128, 6)
