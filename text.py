

import numpy as np
from vispy import io

# keep bitmaps in atlas
# load atlas, pass in number of cols and rows

def load_font(path, tile_w, tile_h):
    image = io.imread(path)
    (image_w, image_h, _) = image.shape
    cols = int(image_w/tile_w)
    rows = int(image_h/tile_h)
    font = {}
    font['tile_w'] = tile_w
    font['tile_h'] = tile_h
    for r in range(rows):
        for c in range(cols):
            n = chr(c+r*cols)
            print("adding {}, {} as '{}', number {}".format(r, c, n, c+c*r))
            font[n] = image[r*tile_h:r*tile_h+tile_h, c*tile_w:c*tile_w+tile_w, :]
    #print(font.keys())
    return font


def arrange(font, string):
    image = np.zeros((font['tile_h']*1, font['tile_w']*len(string), 3), dtype=np.uint8)
    for i, letter in enumerate(string):
        image[0:font['tile_h'], i*font['tile_w']:i*font['tile_w']+font['tile_w'], :] = font[letter]
    return image


def dump_test(font):
    io.imsave("texrender.png", arrange(font, "hello"))


if __name__ == '__main__':
    dump_test(load_font('images/font.png', 18, 18))
